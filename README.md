# Link2Drive (Rclone to Multi-Remote)

A powerful GitHub Action to download files from direct links and upload them to any remote configured in your Rclone config (Google Drive, Mega, Dropbox, S3, etc.).

## 🚀 Features

- **Multi-Remote**: Supports any remote defined in your Rclone config.
- **Fast Downloads**: Uses `aria2c` with multi-threaded downloading.
- **Auto-Process**: Automatically starts when you update the `urls.txt` file.
- **Manual Input**: One-off downloads directly from the Actions tab.
- **Verbose Debugging**: Detailed logs if an upload fails.

## 🛠️ Setup Instructions

### 1. Generate Rclone Config
1. Install Rclone on your local machine.
2. Run `rclone config` and follow the steps to create your remotes (e.g., call one `gdrive`).
3. Find your `rclone.conf` file:
   - **Windows**: `%AppData%\rclone\rclone.conf`
   - **Linux/Mac**: `~/.config/rclone/rclone.conf`
4. Copy the **entire** content of that file.

### 2. Add GitHub Secret
1. Go to your repository **Settings** > **Secrets and variables** > **Actions**.
2. Click **New repository secret**.
3. Name it: `RCLONE_CONFIG`.
4. Paste your `rclone.conf` content into the value box.

### 3. Usage

#### Method A: Automatic (Recommended)
1. Open the `urls.txt` file in this repository.
2. Paste your direct links (one per line).
3. Commit and Push the changes. 
4. **The Action will start automatically** and upload to your default remote.

#### Method B: Manual
1. Go to the **Actions** tab.
2. Select **Download & Upload (Multi-Remote)**.
3. Click **Run workflow**.
4. Enter your **Remote Name** and the **Link**, then click Run.

## 📝 Customization
You can change the default remote for automatic runs by editing the `rclone_remote` value in `.github/workflows/upload.yml`.

## 📝 License
MIT
