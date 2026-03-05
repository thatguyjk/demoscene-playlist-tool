from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from demoscene_playlist_tool.core.executor import Executor


class ExecutorThread(QThread):
    entry_started = pyqtSignal(str)
    playback_error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, paths: list[Path]) -> None:
        super().__init__()
        self._paths = paths
        self._start_index: int | None = None
        self._executor = Executor(
            on_started=lambda p: self.entry_started.emit(str(p)),
            on_error=lambda p, err: self.playback_error.emit(f"Failed to launch {p}: {err}"),
        )

    def set_start_index(self, index: int) -> None:
        """Set the index to start playback from."""
        self._start_index = index

    def run(self) -> None:
        if self._start_index is not None and 0 <= self._start_index < len(self._paths):
            # Start from the specified index
            paths_to_run = self._paths[self._start_index:]
        else:
            # Start from the beginning or handle invalid index
            paths_to_run = self._paths

        try:
            self._executor.run(paths_to_run)
        except Exception as error:
            # Keep UI state consistent even if an unexpected runtime exception occurs.
            self.playback_error.emit(f"Playback failed: {error}")
        finally:
            self.finished.emit()
