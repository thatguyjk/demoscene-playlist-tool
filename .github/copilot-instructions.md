# Copilot Instructions

## Project Overview

`demoscene-playlist-tool` is a Python application that lets users build and manage playlists of executable files (demoscene demos) that are launched sequentially for continuous playback. The UI is built with **PyQt6**. Primary target OS is **Windows**; distributed cross-platform via **PyInstaller**.

## Architecture

The core responsibilities are:

- **Playlist management** – adding, removing, and reordering executable entries in a playlist
- **Execution loop** – launching each executable in sequence, waiting for it to finish, then advancing to the next
- **Persistence** – saving and loading playlists (file paths + any metadata) between sessions
- **UI layer** – PyQt6 widgets; keep business logic separate from Qt code so it remains testable without a display

## Conventions

- Dependency management uses **uv** (not pip directly); `uv sync` installs from `pyproject.toml`
- Executables in the playlist are referenced by filesystem path
- The execution model is sequential: one demo runs to completion before the next is launched
- Windows is the primary target; avoid Unix-only APIs in the execution layer
- PyInstaller is used for packaging — avoid dynamic imports or `__file__`-relative hacks that break frozen builds

## Commands

```bash
# Install dependencies
uv sync

# Run the tool
uv run python -m demoscene_playlist_tool

# Run all tests
uv run pytest

# Run a single test
uv run pytest tests/test_<module>.py::test_<name>

# Lint
uv run ruff check .

# Build distributable (from project root)
uv run pyinstaller demoscene_playlist_tool.spec
```
