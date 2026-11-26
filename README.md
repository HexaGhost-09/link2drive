# Link2Drive

Download direct HTTP(S) links and BitTorrent magnet links with **aria2c**, then upload the files to your Google Drive using the official Drive API. Runs on GitHub Actions.

**No rclone.**

## Configure Google Drive

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project and enable **Google Drive API**.
2. Configure the OAuth consent screen and create an OAuth client ID (Desktop app).
3. Generate a refresh token for your Google account with the scope `https://www.googleapis.com/auth/drive`.
4. In GitHub → Settings → Secrets and variables → Actions, add:

| Secret | Value |
|---|---|
| `GDRIVE_CLIENT_ID` | OAuth client ID |
| `GDRIVE_CLIENT_SECRET` | OAuth client secret |
| `GDRIVE_REFRESH_TOKEN` | OAuth refresh token |
| `GDRIVE_FOLDER_ID` | Optional parent folder ID; leave unset to use My Drive root |

Use your own Google account OAuth credentials for personal My Drive. Do not use a service account for a normal personal Drive.

## Run

- **Manual:** Actions → Link2Drive → Run workflow. Paste one direct URL or magnet link. Leave it blank to process all entries in `links.txt`.
- **Automatic:** Add new links to `links.txt` and push to `main`. Only newly added lines are processed.
- Set ZIP to upload one archive instead of individual files.
- Set Share to create public viewer links. Anyone with the link will be able to access those files.

## Performance and limits

aria2c uses segmented, multi-connection downloads where the source server supports them. Magnet downloads use aria2's BitTorrent engine. Drive uploads use resumable 8 MiB chunks so interrupted transfers can recover during the run.

Actual speed depends on the source, peers, GitHub Actions runner, Google Drive and their quotas. GitHub-hosted runners have finite disk space and job time. Google Drive API does not add storage to your account; normal Drive storage limits still apply.

## Security

Keep OAuth credentials in GitHub Actions Secrets. Never commit refresh tokens, client secrets, or private download URLs to the repository. Public link sharing is optional and disabled by default.
