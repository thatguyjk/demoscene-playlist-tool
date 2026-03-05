# 🎬 Demoscene Playlist Tool

> *Sit back, relax, and let the pixels wash over you.*

A desktop app for queuing up demoscene executables and watching them play back-to-back — no clicking, no fussing, just pure uninterrupted demo goodness.

## What is this?

If you've ever wanted to host a demoshow, run a long demo night, or just marathon your favourite releases without babysitting your keyboard, this is the tool for you. Add your demos, arrange them in whatever order sparks joy, hit **Play**, and walk away.

Built with Python and PyQt6. Windows is the primary target (because that's where the `.exe`s live), but it'll run anywhere Python does.

## Features

- 📂 **Add executables** to a playlist from anywhere on your filesystem
- ↕️ **Reorder entries** with up/down controls
- 💾 **Save & load playlists** as plain JSON files — easy to share, easy to edit
- ▶️ **Play** the entire playlist sequentially, one demo after another
- ⏹️ **Stop** playback at any time
- 📡 **Status bar** shows which demo is currently running

## Getting Started

### Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

### Install & run

```bash
git clone https://github.com/thatguyjk/demoscene-playlist-tool.git
cd demoscene-playlist-tool
uv sync
uv run demoscene-playlist-tool
```

## Usage

1. Click **Add** to pick an executable from your disk
2. Use **▲ / ▼** to reorder entries
3. Use **File → Save Playlist** to save your lineup as a `.json` file
4. Use **File → Open Playlist** to reload a saved lineup later
5. Hit **▶ Play** and enjoy the show

## Development

```bash
# Run tests
uv run pytest

# Run a single test
uv run pytest tests/test_playlist.py::test_save_and_load

# Lint
uv run ruff check .
```

## Building a distributable

```bash
uv run pyinstaller demoscene_playlist_tool.spec
```

## Playlist format

Playlists are plain JSON — nothing fancy:

```json
{
  "entries": [
    "C:\\demos\\elevated.exe",
    "C:\\demos\\fr-08.exe",
    "C:\\demos\\debris.exe"
  ]
}
```

---

*Made with love for the demoscene community. Greetings to everyone still pushing pixels!* 🖥️✨
