import subprocess
from collections.abc import Callable
from pathlib import Path


class Executor:
    """Runs playlist entries sequentially, calling back between each."""

    def __init__(
        self,
        on_started: Callable[[Path], None] | None = None,
        on_error: Callable[[Path, OSError], None] | None = None,
    ) -> None:
        self.on_started = on_started
        self.on_error = on_error

    def run(self, paths: list[Path]) -> None:
        for path in paths:
            if self.on_started:
                self.on_started(path)
            try:
                subprocess.run([str(path)], check=False)
            except OSError as error:
                if self.on_error:
                    self.on_error(path, error)
