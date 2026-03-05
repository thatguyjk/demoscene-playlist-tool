from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from demoscene_playlist_tool.core.executor import Executor


class ExecutorThread(QThread):
    entry_started = pyqtSignal(str)  # emits path string of the current entry
    finished = pyqtSignal()

    def __init__(self, paths: list[Path]) -> None:
        super().__init__()
        self._paths = paths
        self._executor = Executor(on_started=lambda p: self.entry_started.emit(str(p)))

    def run(self) -> None:
        self._executor.run(self._paths)
        self.finished.emit()

    def stop(self) -> None:
        self._executor.stop()
