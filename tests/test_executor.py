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


def test_missing_executable_reports_error_and_continues():
    started_callback = MagicMock()
    error_callback = MagicMock()
    executor = Executor(on_started=started_callback, on_error=error_callback)
    paths = [Path("/missing.exe"), Path("/next.exe")]

    with patch(
        "demoscene_playlist_tool.core.executor.subprocess.run",
        side_effect=[FileNotFoundError("missing"), None],
    ) as run_mock:
        executor.run(paths)

    assert run_mock.call_count == 2
    assert started_callback.call_count == 2
    error_callback.assert_called_once()
    assert error_callback.call_args.args[0] == Path("/missing.exe")
