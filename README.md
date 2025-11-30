<div align="center">
  <img src="https://i.ibb.co/RGJnsfC6/monkey-d-luffy-red-3840x2160-24473.png" alt="AutoAnimePro Banner" width="100%" style="border-radius: 10px;">

  # 🎬 Argons Encoder

  **The Ultimate Anime Automation & Encoding Bot**

  [![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Pyrogram](https://img.shields.io/badge/Pyrogram-v2.0-yellow?style=for-the-badge&logo=telegram&logoColor=white)](https://docs.pyrogram.org/)
  [![FFmpeg](https://img.shields.io/badge/FFmpeg-Encoding-green?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
  [![License](https://img.shields.io/badge/License-MIT-red?style=for-the-badge)](LICENSE)

  <p align="center">
    <a href="#-key-features">Features</a> •
    <a href="#-installation">Installation</a> •
    <a href="#-commands">Commands</a> •
    <a href="#-project-structure">Structure</a>
  </p>
</div>

---

## 🚀 Key Features

### 🎥 **Professional Encoding**
- **High-Fidelity Output**: Uses **FFmpeg** with optimized presets for crystal clear video.
- **Smart Containers**: Defaults to **MKV** for maximum compatibility and subtitle preservation.
- **Subtitle Copy**: Automatically copies subtitle streams (`-c:s copy`) without transcoding.
- **Quality Steps**: Tracks progress across multiple resolution steps (e.g., Quality 1/3).

### ⚡ **Intelligent Queue System**
- **FIFO Processing**: Ensures fair, sequential processing of all user jobs.
- **Persistence**: Automatically restores the queue and active jobs after a bot restart.
- **Concurrency**: Handles **sequential encoding** and **concurrent uploads** (up to 2) for maximum efficiency.

### 🎨 **Premium User Experience**
- **Rich UI**: Beautiful, blockquote-based progress bars with real-time stats (FPS, Bitrate, ETA).
- **Interactive Controls**: Pause, Resume, and Cancel jobs directly from the progress message.
- **Smart Notifications**:
  - **Separate Upload Message**: Keeps chat clean by deleting the upload progress message upon completion.
  - **Pause Details**: Shows file name, settings, and user info when a job is paused.
- **Logging**: Detailed logs of every encode sent to a dedicated channel.

### 🛠️ **Customization**
- **Watermarks**: Add custom text or image watermarks to your videos. Supports positioning, opacity, and timing.
- **Metadata**: Manage video metadata (Title, Author, etc.) to keep your library organized.

### 🛠️ **Robust Management**
- **User Database**: Automatically registers users on `/start`.
- **Startup Cleanup**: Wipes temporary `downloads/` to prevent disk bloat.
- **Resource Efficient**: Uses `uvloop` for ultra-fast async I/O.

### 🛡️ **Admin Features**
- **Broadcast System**: Send messages (Normal/Pin) to all users with real-time stats.
- **Admin Panel**: Interactive GUI for the owner to add/remove admins easily.
- **User Management**: Auto-cleanup of blocked/deleted accounts during broadcasts.

---

## 🛠️ Installation

### Prerequisites
- **Python 3.9+**
- **FFmpeg** (installed and in PATH)
- **MongoDB** (Database)
- **Telegram Bot Token** & **API Keys**

### 💻 Local Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Itzmepromgitman/autoanimepro.git
   cd autoanimepro
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   Create a `.env` file in the root directory:
   ```env
   TG_BOT_TOKEN=your_bot_token
   APP_ID=your_app_id
   API_HASH=your_api_hash
   OWNER_ID=your_telegram_id
   CHANNEL_ID=-100xxxxxxxx  # Your Log Channel ID
   DATABASE_URL=your_mongodb_uri
   DATABASE_NAME=Cluster0
   TG_BOT_WORKERS=4
   ```

4. **Run the Bot**
   ```bash
   bash start.sh
   ```

### 🐳 Docker Deployment

Deploy effortlessly with Docker:

```bash
# 1. Build Image
docker build -t autoanimepro .

# 2. Run Container
docker run -d --env-file .env --name encoder_bot autoanimepro
```

---

## 🤖 Commands

| Command | Description | Permission |
| :--- | :--- | :--- |
| `/start` | Initialize the bot & register user. | Everyone |
| `/settings` | Configure video settings (Codec, CRF, Resolution). | Everyone |
| `/queue` | View the current job queue. | Everyone |
| `/stats` | View system and bot statistics. | Everyone |
| `/ss` | Generate screenshots from video. | Everyone |
| `/cancel <id>` | Cancel a specific job. | Owner/User |
| `/clear` | Clear your queued jobs. | Admin/User |
| `/cancelall` | Cancel **ALL** active jobs. | Owner Only |
| `/restart` | Restart the bot server. | Owner Only |
| `/log` | Retrieve the bot's log file. | Owner Only |
| `/shell` | Execute shell commands. | Owner Only |
| `/broadcast` | Broadcast message to users. | Admin Only |
| `/admin` | Open Admin Panel. | Owner Only |
| `/info` | Get detailed job info. | Admin Only |
| `/help` | Access the help manual. | Everyone |

---

## 📁 Project Structure

```
autoanimepro/
├── bot/
│   ├── func/           # Core Logic
│   │   ├── pyroutils/  # Progress Bar Utils
│   │   ├── encode.py   # Main Encoding Engine
│   │   ├── queue_manager.py
│   │   ├── download_manager.py
│   │   ├── upload_manager.py
│   │   └── ffmpeg_utils.py
│   ├── utils/          # Helpers
│   │   ├── restart.py
│   │   └── shell.py
│   ├── config.py       # Config Loader
│   ├── logger.py       # Logging System
│   └── __main__.py     # Entry Point
├── plugins/            # Handlers
│   ├── admin.py
│   ├── encode.py
│   ├── query.py
│   ├── queue.py
│   ├── settings.py
│   └── start.py
├── Dockerfile          # Docker Config
├── requirements.txt    # Dependencies
└── start.sh            # Startup Script
```

---

## 📜 License

This project is licensed under the **MIT License**.

<div align="center">
  <br>
  <i>Built with ❤️ by <a href="https://t.me/ReactiveArgon"><b>Argon</b></a></i>
</div>