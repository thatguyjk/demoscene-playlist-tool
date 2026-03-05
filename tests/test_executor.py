from pathlib import Path
from unittest.mock import MagicMock, patch

from demoscene_playlist_tool.core.executor import Executor


def test_on_started_called_for_each_entry():
    callback = MagicMock()
    executor = Executor(on_started=callback)
    paths = [Path("/a.exe"), Path("/b.exe")]

    with patch("demoscene_playlist_tool.core.executor.subprocess.run"):
        executor.run(paths)

    assert callback.call_count == 2
    callback.assert_any_call(Path("/a.exe"))
    callback.assert_any_call(Path("/b.exe"))


def test_stop_halts_execution():
    calls = []

    def on_started(p):
        calls.append(p)
        executor.stop()

    executor = Executor(on_started=on_started)
    paths = [Path("/a.exe"), Path("/b.exe"), Path("/c.exe")]

    with patch("demoscene_playlist_tool.core.executor.subprocess.run"):
        executor.run(paths)

    assert len(calls) == 1
