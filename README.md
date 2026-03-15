# Link2Drive (Rclone to Multi-Remote)

A powerful GitHub Action to download files from direct links and upload them to any remote configured in your Rclone config (Google Drive, Mega, Dropbox, Internet Archive, Gofile, etc.).

## 🚀 Features

- **Multi-Remote**: Supports any remote defined in your `rclone.conf`.
- **Fast Downloads**: Uses `aria2c` with multi-threaded downloads.
- **Easy Link Editing**: Add your links to `urls.txt` (one per line).
- **Manual Input**: Provide a single link when running the Action for one-off downloads.
- **Verbose Logging**: Debugging tools to see exactly why an upload might fail.

## 📁 Available Remotes in your `rclone.conf`

- `internet-archive`
- `internet-archive-anon`
- `ia-s3`
- `Mega - Ben` (Mega)
- `Dropbox - Zegroh` (Dropbox)
- `GDrive - rotatos210` (Google Drive)
- `GDrive Ben` (Google Drive)
- `Gofile` (Gofile)

## 🛠️ Setup Instructions

### 1. Setup GitHub Secret
1. Go to your repository **Settings** > **Secrets and variables** > **Actions**.
2. Click **New repository secret**.
3. Name it: `RCLONE_CONFIG`.
4. Paste the entire content of your `rclone.conf` file into the value box.

### 2. Run the Workflow
1. Go to the **Actions** tab in your repository.
2. Select **Download & Upload (Multi-Remote)**.
3. Click **Run workflow**.
4. Enter the **Remote Name** (e.g., `GDrive Ben`) and the link you want to download.

## 📝 Editing Links
You can edit `urls.txt` and commit the changes. The Action will process every link in that file if the `manual_url` field is left empty when running the workflow.

## 📝 License
MIT
