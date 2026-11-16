# Uploader V5.4 — Smart Batch Downloads

Paste up to 20 direct HTTP/HTTPS download URLs into the **Multiple Links** field, one URL per line. V5 checks each source's size, downloads files in size-based concurrent batches, uploads each batch to the selected rclone remote, and deletes the batch's local temporary files before starting the next batch.

## Adaptive download limits

| Detected file size | Simultaneous downloads |
|---|---:|
| Over 3 GB | 1 |
| Over 500 MB up to 3 GB | 5 |
| 500 MB or smaller | 10 |
| Size cannot be determined | 1 |

Sizes use decimal bytes (1 GB = 1,000,000,000 bytes). The workflow checks file size with HTTP HEAD and falls back to a one-byte Range request. If the server does not reveal its size, the file is processed alone to reduce disk-space risk. Each staged batch is also capped at 8 GB total, so a five-file medium batch may be split into smaller groups when needed to protect runner disk space.

## Batch lifecycle

1. The workflow probes the URLs and groups files by size.
2. It downloads up to the allowed number of files concurrently.
3. It uploads the downloaded files to `<remote>:Downloads/` using rclone.
4. After every file in that batch uploads successfully, the temporary batch directory is deleted.
5. The next batch begins.

If a download or upload fails, the workflow stops rather than deleting a batch that has not uploaded successfully. GitHub Actions also removes the runner workspace when the job ends.

## Google Drive privacy

Uploads are **private by default**. The workflow does not run `rclone link`, create public share links, or change Google Drive permissions. Files inherit the permissions of the destination folder and Google account. Share them manually in Google Drive if needed.

## One-time setup

1. Rotate credentials in any previously committed `rclone.conf`; revoke or refresh exposed credentials/tokens.
2. Create a fresh rclone configuration locally with the remote you want to use (normally `gdrive`).
3. In GitHub, open **Settings → Secrets and variables → Actions → New repository secret**.
4. Add a repository secret named **`RCLONE_CONFIG_CONTENT`** containing the complete fresh configuration.
5. Open **Actions → Uploader V5 - Smart Batch Downloads → Run workflow**.
6. Paste one to 20 direct file URLs into **Multiple Links**, each on its own line.

## Inputs

- `direct_urls`: one to 20 direct HTTP/HTTPS file URLs, one per line. Blank lines and lines beginning with `#` are ignored.
- `remote_name`: rclone remote name from the secret; defaults to `gdrive`.

## Limitations

- URLs must point directly to downloadable files, not webpages with download buttons.
- Sources requiring browser cookies or authentication not embedded in the URL may fail.
- Size detection depends on the source server providing Content-Length or Content-Range. Unknown-size files are downloaded one at a time.
- Duplicate filenames may overwrite each other in the destination folder; rename source files or separate runs to avoid collisions.
- Transfers share the GitHub Actions six-hour job limit.
- ZIP and torrent/magnet modes are not included.
