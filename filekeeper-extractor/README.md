# FileKeeper Link Extractor

This is a separate GitHub Actions workflow; it does not modify the Link2Drive uploader workflows or its root `urls.txt`.

## Use

1. Add FileKeeper file-page URLs or a FitGirl PrivateBin URL to `filekeeper-extractor/links.txt`, one per line.
2. Commit the changes.
3. Open **Actions** → **FileKeeper Link Extractor** → **Run workflow**.
4. Open the completed run and download the `filekeeper-extracted-links` artifact.
5. The artifact contains `filekeeper_links.txt`.

The workflow runs manually and retains the artifact for 3 days. CAPTCHA-protected pages are skipped; no CAPTCHA solver is included. Extracted CDN links may expire. Do not commit private paste keys, passwords, or account credentials to a public repository.
