# Changelog

All notable changes to the **Link2Drive** project will be documented in this file.

## [2.5.0] - 2026-03-16

### 🚀 Added
- **Auto-Zipping**: Automatically packs multiple files or folders into a single `.zip` archive before uploading. This keeps your cloud storage organized and ensures no files are missed from complex torrents.
- **Smart Archive Naming**: Zip files are named based on the content to make them easy to find.

## [2.0.0] - 2026-03-15

### 🚀 Added
- **Torrent & Magnet Support**: Added the ability to download via Magnet links and `.torrent` files.
- **Smart Speed Monitoring**: Implemented a protective monitoring loop for torrents.
- **Slow Torrent Protection**: If a file > 1GB is slower than 1MB/s, the Action automatically stops to save GitHub quota.
- **Live Progress Tracking**: Real-time logs showing Percentage (%), Speed, and Total Size for all transfers.
- **Improved UI/UX**: Workflow dispatch inputs now pre-filled with the most common remotes.

## [1.0.0] - 2026-03-15

### 🚀 Added
- **Initial Release**: Core functionality to transfer files from direct links to cloud storage.
- **Rclone Integration**: Support for all Rclone-compatible clouds (GDrive, Mega, Dropbox, etc.).
- **Automatic Triggers**: Workflow runs immediately upon updating `urls.txt`.
- **Manual Trigger**: "Run Workflow" button support for one-off transfers.
- **Smart Filename Detection**: Preserves original names like `.apk` and `.mp4` using server headers.
- **Pre-flight Check**: Verifies cloud connectivity before starting downloads.
- **Automatic Verbose Debugging**: Retries failed uploads with full logs to identify issues.
- **Setup Script**: `setup_rclone.ps1` for easy local configuration on Windows.
- **Generic README**: Instructions tailored for public/personal use.
