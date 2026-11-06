# Uploader V5 — Direct URL Streaming

V5 streams a direct HTTP/HTTPS download into an rclone remote. It does not save the complete file on the GitHub runner.

## What it does

- Uses a Rust program (`uploader-v5`) to read the source response as a byte stream.
- Pipes the stream into `rclone rcat`, which uploads to the selected remote.
- Uses the source Content-Length when available so rclone can preallocate and stream the upload.
- Detects the filename from Content-Disposition, falling back to the URL path. You can override it in the workflow inputs.
- If the source connection drops, it attempts to resume with an HTTP Range request (up to five retries). The source must support Range requests for this recovery to work.
- Optionally creates a share link with `rclone link`.

## One-time setup

1. **Rotate credentials in the existing `rclone.conf`.** The repository copy contains credentials/tokens and must be treated as compromised. Revoke/refresh the exposed credentials with their providers. Do not reuse the committed file.
2. Create a fresh rclone configuration locally with the remote you want to use (normally `gdrive`).
3. In GitHub, open **Settings → Secrets and variables → Actions → New repository secret**.
4. Create a secret named **`RCLONE_CONFIG_CONTENT`**. Paste the complete fresh rclone configuration as its value.
5. Run **Actions → Uploader V5 - Direct URL Streaming → Run workflow**.

## Inputs

- `direct_url`: direct HTTP/HTTPS file URL (not a webpage containing a download button).
- `remote_name`: remote name from the secret config; defaults to `gdrive`.
- `filename`: optional filename override.
- `link_sharing`: optionally create a link after upload.

The remote destination is `<remote>:Downloads/<filename>`.

## Important limitations

- This is a streaming transfer: runner disk use stays small, but network traffic and job time still apply.
- GitHub-hosted jobs have a finite execution limit (the workflow is set to six hours). A 100 GB transfer must finish within that window.
- A source that blocks automated requests, requires browser cookies, or does not provide a direct file response may fail.
- Automatic source-resume requires HTTP Range support. If the GitHub job itself is cancelled or the rclone process exits, the transfer must be started again; this workflow does not persist an upload session between separate workflow runs.
- The workflow currently targets rclone remotes that support streaming uploads. The `--drive-chunk-size` setting is intended for Google Drive.
- ZIP mode and torrent/magnet downloads are intentionally not included in V5; those workflows need local staging or a separate streaming archive/torrent design.
