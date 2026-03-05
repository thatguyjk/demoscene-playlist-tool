from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QListWidget, QPushButton,
    QHBoxLayout, QFileDialog, QStatusBar,
)

from demoscene_playlist_tool.core.playlist import Playlist
from demoscene_playlist_tool.ui.executor_thread import ExecutorThread


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Demoscene Playlist Tool")
        self.resize(600, 400)

        self._playlist = Playlist()
        self._thread: ExecutorThread | None = None

        self._selected_entry: int | None = None

        self._list = QListWidget()

        add_btn = QPushButton("Add")
        remove_btn = QPushButton("Remove")
        up_btn = QPushButton("▲")
        down_btn = QPushButton("▼")
        self._play_btn = QPushButton("▶  Play")

        add_btn.clicked.connect(self._add_entry)
        remove_btn.clicked.connect(self._remove_entry)
        up_btn.clicked.connect(self._move_up)
        down_btn.clicked.connect(self._move_down)
        self._play_btn.clicked.connect(self._play)
        self._list.currentRowChanged.connect(self._set_selected)

        edit_row = QHBoxLayout()
        for w in (add_btn, remove_btn, up_btn, down_btn):
            edit_row.addWidget(w)

        play_row = QHBoxLayout()
        play_row.addWidget(self._play_btn)

        layout = QVBoxLayout()
        layout.addWidget(self._list)
        layout.addLayout(edit_row)
        layout.addLayout(play_row)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self._status = QStatusBar()
        self.setStatusBar(self._status)

        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        file_menu.addAction("Open Playlist…", self._open_playlist)
        file_menu.addAction("Save Playlist…", self._save_playlist)

    # --- playlist editing ---

    def _add_entry(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select executable")
        if path:
            self._playlist.add(Path(path))
            self._list.addItem(path)

            if self._selected_entry is None:
                self._selected_entry = 0

    def _remove_entry(self) -> None:
        row = self._list.currentRow()
        if row >= 0:
            self._playlist.remove(row)
            self._list.takeItem(row)

            if self._list.count() == 0:
                self._list.setCurrentRow(-1)
            else:
                self._list.setCurrentRow(min(row, self._list.count() - 1))

            # Ensure internal state is updated even if Qt does not emit row-changed.
            self._set_selected()

    def _move_up(self) -> None:
        row = self._list.currentRow()
        if row > 0:
            self._playlist.move(row, row - 1)
            item = self._list.takeItem(row)
            self._list.insertItem(row - 1, item)
            self._list.setCurrentRow(row - 1)

    def _move_down(self) -> None:
        row = self._list.currentRow()
        if row >= 0 and row < self._list.count() - 1:
            self._playlist.move(row, row + 1)
            item = self._list.takeItem(row)
            self._list.insertItem(row + 1, item)
            self._list.setCurrentRow(row + 1)

    def _set_selected(self, row: int | None = None) -> None:
        current_row = self._list.currentRow() if row is None else row
        self._selected_entry = current_row if current_row >= 0 else None

    # --- save / load ---

    def _open_playlist(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Playlist", filter="Playlist files (*.json)"
        )
        if not path:
            return
        try:
            self._playlist = Playlist.load(Path(path))
        except (OSError, ValueError) as error:
            self._status.showMessage(f"Failed to load playlist: {error}")
            return

        self._list.clear()
        for entry in self._playlist.entries:
            self._list.addItem(str(entry.path))

        if self._list.count() > 0:
            self._list.setCurrentRow(0)
        else:
            self._list.setCurrentRow(-1)

        self._status.showMessage(f"Loaded {path}")

    def _save_playlist(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Playlist", filter="Playlist files (*.json)"
        )
        if not path:
            return
        if not path.endswith(".json"):
            path += ".json"
        self._playlist.save(Path(path))
        self._status.showMessage(f"Saved {path}")

    # --- playback ---

    def _play(self) -> None:
        if not self._playlist.entries:
            return
        paths = [e.path for e in self._playlist.entries]
        self._thread = ExecutorThread(paths)

        if self._selected_entry is not None and 0 <= self._selected_entry < len(paths):
            self._thread.set_start_index(self._selected_entry)

        self._thread.entry_started.connect(
            lambda p: self._status.showMessage(f"Now playing: {p}")
        )
        self._thread.playback_error.connect(self._status.showMessage)
        self._thread.finished.connect(self._on_playback_finished)
        self._thread.start()
        self._play_btn.setEnabled(False)

    def _on_playback_finished(self) -> None:
        self._play_btn.setEnabled(True)
        self._status.showMessage("Playback finished")
