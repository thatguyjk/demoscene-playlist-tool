from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from demoscene_playlist_tool.core.executor import Executor


class ExecutorThread(QThread):
    entry_started = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, paths: list[Path]) -> None:
        super().__init__()
        self._paths = paths
        self._start_index: int | None = None
        self._executor = Executor(on_started=lambda p: self.entry_started.emit(str(p)))

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
            
        self._executor.run(paths_to_run)
        self.finished.emit()
