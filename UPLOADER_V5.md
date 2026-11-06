# Uploader V5.1 — Prebuilt Rust binary

V5.1 is a separate workflow from V5. It downloads a precompiled Linux x86_64 executable at upload time, so normal upload runs do not install Rust, download crates, or compile the program.

## First-time setup

1. Open **Actions → Build and publish Uploader V5.1 binary**.
2. Select **Run workflow** and wait for it to finish successfully.
3. This creates the GitHub Release `v5.1.0` with the binary `link2drive-stream-linux-x86_64` and its SHA-256 checksum.
4. Ensure the repository Actions secret `RCLONE_CONFIG_CONTENT` contains a newly rotated rclone configuration. Do not reuse any credentials previously pasted into chat or committed to the repository.

## Uploading

1. Open **Actions → Uploader V5.1 - Prebuilt Direct URL Streaming**.
2. Enter a direct HTTP/HTTPS file URL, remote name (normally `gdrive`), optional filename, and link-sharing preference.
3. Run the workflow.

The uploader saves the download stream directly into `rclone rcat`; it does not stage the complete file on the runner. The regular upload workflow downloads the prebuilt executable from the public GitHub Release.

## Updating the binary

When the Rust source changes, update the release asset by running **Build and publish Uploader V5.1 binary** again. The workflow publishes/replaces the asset for release tag `v5.1.0`.

## Notes

- The prebuilt binary targets GitHub-hosted Ubuntu x86_64 runners.
- The first build/release is required before the V5.1 upload workflow can run.
- The source URL must be a direct HTTP/HTTPS response. HTTP Range support is required for recovery from a mid-stream download interruption.
- The workflow still has the GitHub-hosted job time limit; prebuilding removes compile time, not transfer time.
- The uploader uses rclone for remote access. The rclone config must include the chosen remote.
