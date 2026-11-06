use anyhow::{Context, Result, bail};
use futures_util::StreamExt;
use percent_encoding::percent_decode_str;
use reqwest::header::{CONTENT_DISPOSITION, CONTENT_RANGE, RANGE};
use std::{env, process::Stdio};
use tokio::{
    io::AsyncWriteExt,
    process::Command,
    time::{sleep, Duration},
};
use url::Url;

fn safe_filename(input: &str) -> String {
    let cleaned: String = input
        .chars()
        .filter(|c| !c.is_control() && *c != '/' && *c != '\\')
        .collect();
    let cleaned = cleaned.trim().trim_matches('.');
    if cleaned.is_empty() || cleaned == "." || cleaned == ".." {
        "download.bin".to_string()
    } else {
        cleaned.to_string()
    }
}

fn filename_from_headers(value: Option<&reqwest::header::HeaderValue>) -> Option<String> {
    let value = value?.to_str().ok()?;

    for part in value.split(';').map(str::trim) {
        if let Some(raw) = part.strip_prefix("filename*=") {
            let raw = raw.trim_matches('"');
            let encoded = raw.split_once("''").map(|(_, v)| v).unwrap_or(raw);
            let decoded = percent_decode_str(encoded).decode_utf8().ok()?;
            return Some(safe_filename(decoded.as_ref()));
        }
    }

    for part in value.split(';').map(str::trim) {
        if let Some(raw) = part.strip_prefix("filename=") {
            return Some(safe_filename(raw.trim().trim_matches('"')));
        }
    }
    None
}

fn filename_from_url(raw_url: &str) -> String {
    Url::parse(raw_url)
        .ok()
        .and_then(|url| {
            url.path_segments()
                .and_then(|mut segments| segments.next_back())
                .map(|segment| percent_decode_str(segment).decode_utf8_lossy().to_string())
        })
        .filter(|name| !name.is_empty())
        .map(|name| safe_filename(&name))
        .unwrap_or_else(|| "download.bin".to_string())
}

#[tokio::main]
async fn main() -> Result<()> {
    let mut args = env::args().skip(1);
    let source_url = args.next().context("Usage: link2drive-stream <direct-url> <remote-name> [filename]")?;
    let remote_name = args.next().context("Missing rclone remote name")?;
    let override_name = args.next().unwrap_or_default();

    let parsed = Url::parse(&source_url).context("Invalid direct URL")?;
    if parsed.scheme() != "http" && parsed.scheme() != "https" {
        bail!("Only HTTP and HTTPS direct URLs are supported");
    }
    if remote_name.trim().is_empty() || remote_name.contains(':') || remote_name.contains('/') {
        bail!("Invalid remote name");
    }

    let client = reqwest::Client::builder()
        .user_agent("link2drive-uploader/5.0")
        .connect_timeout(Duration::from_secs(45))
        .timeout(None)
        .redirect(reqwest::redirect::Policy::limited(10))
        .build()?;

    println!("Connecting to direct download URL...");
    let response = client.get(&source_url).send().await.context("Download request failed")?;
    if !response.status().is_success() {
        bail!("Source returned HTTP {}", response.status());
    }

    let total_size = response.content_length();
    let filename = if !override_name.trim().is_empty() {
        safe_filename(&override_name)
    } else {
        filename_from_headers(response.headers().get(CONTENT_DISPOSITION))
            .unwrap_or_else(|| filename_from_url(&source_url))
    };

    let target = format!("{}:Downloads/{}", remote_name, filename);
    println!("File name: {}", filename);
    match total_size {
        Some(size) => println!("Source size: {} bytes", size),
        None => println!("Source size: unknown (streaming mode)"),
    }
    println!("Destination: {}", target);

    let mut command = Command::new("rclone");
    command
        .arg("rcat")
        .arg(&target)
        .arg("--progress")
        .arg("--stats")
        .arg("10s")
        .arg("--drive-chunk-size")
        .arg("64M")
        .arg("--streaming-upload-cutoff")
        .arg("64M")
        .stdin(Stdio::piped())
        .stdout(Stdio::inherit())
        .stderr(Stdio::inherit())
        .kill_on_drop(true);

    if let Some(size) = total_size {
        command.arg("--size").arg(size.to_string());
    }

    let mut child = command.spawn().context("Could not start rclone. Is it installed?")?;
    let mut stdin = child.stdin.take().context("Could not open rclone stdin")?;
    let mut transferred: u64 = 0;
    let mut retries: u8 = 0;
    let mut current_response = Some(response);

    loop {
        let active_response = if let Some(first) = current_response.take() {
            first
        } else {
            println!("Retrying source from byte {}...", transferred);
            let resumed = match client
                .get(&source_url)
                .header(RANGE, format!("bytes={}-", transferred))
                .send()
                .await
            {
                Ok(r) => r,
                Err(e) => {
                    retries += 1;
                    if retries > 5 {
                        let _ = child.kill().await;
                        bail!("Could not resume source download after 5 retries: {}", e);
                    }
                    sleep(Duration::from_secs(3)).await;
                    continue;
                }
            };

            if resumed.status() != reqwest::StatusCode::PARTIAL_CONTENT {
                let _ = child.kill().await;
                bail!(
                    "Source did not honor HTTP Range when resuming (expected 206, got {}). This URL cannot be resumed after a network interruption.",
                    resumed.status()
                );
            }
            if let Some(range) = resumed.headers().get(CONTENT_RANGE).and_then(|v| v.to_str().ok()) {
                let expected = format!("bytes {}-", transferred);
                if !range.starts_with(&expected) {
                    let _ = child.kill().await;
                    bail!("Source returned an unexpected Content-Range: {}", range);
                }
            }
            retries = 0;
            resumed
        };

        let mut stream = active_response.bytes_stream();
        let mut stream_failed = false;

        while let Some(item) = stream.next().await {
            match item {
                Ok(chunk) => {
                    if let Err(e) = stdin.write_all(&chunk).await {
                        let _ = child.kill().await;
                        bail!("Upload process stopped while writing data: {}", e);
                    }
                    transferred += chunk.len() as u64;
                    if transferred > 0 && transferred % (512 * 1024 * 1024) < chunk.len() as u64 {
                        println!("Streamed {} MiB", transferred / (1024 * 1024));
                    }
                }
                Err(e) => {
                    eprintln!("Download stream interrupted: {}", e);
                    stream_failed = true;
                    break;
                }
            }
        }

        if !stream_failed {
            break;
        }

        retries += 1;
        if retries > 5 {
            let _ = child.kill().await;
            bail!("Download failed after 5 resume attempts");
        }
        sleep(Duration::from_secs(3)).await;
    }

    drop(stdin);
    let status = child.wait().await.context("Could not wait for rclone")?;
    if !status.success() {
        bail!("rclone upload failed with status {}", status);
    }

    println!("Upload completed: {}", target);

    if let Ok(output_path) = env::var("GITHUB_OUTPUT") {
        use std::io::Write;
        let mut file = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(output_path)?;
        writeln!(file, "filename={}", filename)?;
        writeln!(file, "target={}", target)?;
    }

    Ok(())
}
