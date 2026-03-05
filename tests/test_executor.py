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
