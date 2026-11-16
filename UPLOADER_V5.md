# Uploader V5.3 — Multiple Direct URL Streaming

Uploader V5 accepts multiple direct HTTP/HTTPS download URLs in one workflow run. Paste the URLs into the **Multiple Links** field, one URL per line. Files are streamed sequentially to the selected rclone remote without staging complete files on the GitHub runner.

## Features

- **Multiple Links as Text:** paste up to 20 direct URLs in one run, one URL per line.
- Streams each source response through the Rust uploader into `rclone rcat`.
- Uses source Content-Length when available.
- Detects filenames from Content-Disposition, falling back to the URL path.
- Supports an optional filename override when uploading a single URL.
- Attempts up to five HTTP Range resume retries when the source supports Range requests.
- Uploads to `<remote>:Downloads/<filename>`.

## Google Drive privacy

Uploads are **private by default**. The V5 workflow does not run `rclone link`, create public share links, or change Google Drive permissions. A file remains subject to the permissions of the destination folder and the Google account. If you want to share a file, change its access manually in Google Drive after upload.

## One-time setup

1. Rotate credentials in any previously committed `rclone.conf`; exposed credentials/tokens must be revoked or refreshed.
2. Create a fresh rclone configuration locally with the remote you want to use (normally `gdrive`).
3. In GitHub, open **Settings → Secrets and variables → Actions → New repository secret**.
4. Add a repository secret named **`RCLONE_CONFIG_CONTENT`** containing the complete fresh configuration.
5. Open **Actions → Uploader V5 - Multiple Direct URLs → Run workflow**.
6. Paste one or more direct URLs into **Multiple Links**, each on its own line.

## Inputs

- `direct_urls`: one to 20 direct HTTP/HTTPS file URLs, one per line. Blank lines and lines beginning with `#` are ignored.
- `remote_name`: rclone remote name from the secret; defaults to `gdrive`.
- `filename`: optional override for a single URL only. Leave blank for multiple URLs.

## Limitations

- URLs must point directly to downloadable files, not webpages with download buttons.
- Sources requiring browser cookies or authentication not embedded in the URL may fail.
- Automatic resume requires HTTP Range support.
- Transfers run sequentially and share the workflow's six-hour job limit.
- ZIP and torrent/magnet modes are not included in this V5 workflow.
