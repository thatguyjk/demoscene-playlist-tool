"""Tests for the ExecutorThread UI component."""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from PyQt6.QtWidgets import QApplication  
from PyQt6.QtCore import QThread

from demoscene_playlist_tool.ui.executor_thread import ExecutorThread


@pytest.fixture
def app():
    """Create QApplication instance for testing UI components."""
    return QApplication.instance() or QApplication([])


class TestExecutorThread:
    """Test ExecutorThread functionality."""
    
    def test_initialization(self, app):
        """Test that ExecutorThread initializes properly."""
        paths = [Path("/demo1.exe"), Path("/demo2.exe")]
        thread = ExecutorThread(paths)
        
        assert thread._paths == paths
        assert thread._executor is not None
        assert hasattr(thread, 'entry_started')
        assert hasattr(thread, 'finished')
        
    def test_initialization_empty_paths(self, app):
        """Test initialization with empty path list."""
        thread = ExecutorThread([])
        assert thread._paths == []
        
    @patch('demoscene_playlist_tool.ui.executor_thread.Executor')
    def test_executor_callback_connection(self, mock_executor_class, app):
        """Test that executor on_started callback emits signal."""
        mock_executor = MagicMock()
        mock_executor_class.return_value = mock_executor
        
        paths = [Path("/test.exe")]
        thread = ExecutorThread(paths)
        
        # Verify executor was created with callback
        mock_executor_class.assert_called_once()
        call_args = mock_executor_class.call_args
        assert 'on_started' in call_args.kwargs
        
        # Test that the callback function emits the signal
        with patch.object(thread, 'entry_started') as mock_signal:
            callback = call_args.kwargs['on_started']
            test_path = Path("/test.exe")
            callback(test_path)
            mock_signal.emit.assert_called_once_with(str(test_path))
            
    def test_set_start_index_method_exists(self, app):
        """Test that set_start_index method exists and can be called."""
        thread = ExecutorThread([Path("/test.exe")])
        
        # Should not raise AttributeError
        thread.set_start_index(0)
        
    def test_set_start_index_stores_value(self, app):
        """Test that set_start_index stores the index value."""
        thread = ExecutorThread([Path("/demo1.exe"), Path("/demo2.exe")])
        
        thread.set_start_index(1)
        assert thread._start_index == 1
        
        thread.set_start_index(0)
        assert thread._start_index == 0
        
    def test_set_start_index_defaults_to_none(self, app):
        """Test that start index defaults to None."""
        thread = ExecutorThread([Path("/test.exe")])
        assert thread._start_index is None
        
    @patch('demoscene_playlist_tool.ui.executor_thread.Executor') 
    def test_run_calls_executor_with_full_paths(self, mock_executor_class, app):
        """Test that run calls executor with full path list when no start index."""
        mock_executor = MagicMock()
        mock_executor_class.return_value = mock_executor
        
        paths = [Path("/demo1.exe"), Path("/demo2.exe"), Path("/demo3.exe")]
        thread = ExecutorThread(paths)
        
        with patch.object(thread, 'finished') as mock_finished:
            thread.run()
            
            # Should run with full paths when no start index
            mock_executor.run.assert_called_once_with(paths)
            mock_finished.emit.assert_called_once()
            
    @patch('demoscene_playlist_tool.ui.executor_thread.Executor')
    def test_run_starts_from_index(self, mock_executor_class, app):
        """Test that run starts from specified index."""
        mock_executor = MagicMock()
        mock_executor_class.return_value = mock_executor
        
        paths = [Path("/demo1.exe"), Path("/demo2.exe"), Path("/demo3.exe")]
        thread = ExecutorThread(paths)
        thread.set_start_index(1)
        
        with patch.object(thread, 'finished') as mock_finished:
            thread.run()
            
            # Should start from index 1
            expected_paths = paths[1:]  # [demo2.exe, demo3.exe]
            mock_executor.run.assert_called_once_with(expected_paths)
            mock_finished.emit.assert_called_once() 
            
    @patch('demoscene_playlist_tool.ui.executor_thread.Executor')
    def test_run_start_index_out_of_bounds(self, mock_executor_class, app):
        """Test run behavior when start index is out of bounds."""
        mock_executor = MagicMock()
        mock_executor_class.return_value = mock_executor
        
        paths = [Path("/demo1.exe"), Path("/demo2.exe")]
        thread = ExecutorThread(paths)
        thread.set_start_index(5)  # Out of bounds
        
        with patch.object(thread, 'finished') as mock_finished:
            thread.run()
            
            # Should run with empty list or handle gracefully
            # The exact behavior depends on implementation
            mock_executor.run.assert_called_once()
            mock_finished.emit.assert_called_once()
            
    @patch('demoscene_playlist_tool.ui.executor_thread.Executor')
    def test_run_negative_start_index(self, mock_executor_class, app):
        """Test run behavior with negative start index."""
        mock_executor = MagicMock()
        mock_executor_class.return_value = mock_executor
        
        paths = [Path("/demo1.exe"), Path("/demo2.exe")]
        thread = ExecutorThread(paths)
        thread.set_start_index(-1)
        
        with patch.object(thread, 'finished') as mock_finished:
            thread.run()
            
            # Should handle negative index appropriately
            mock_executor.run.assert_called_once()
            mock_finished.emit.assert_called_once()
            
    def test_signals_exist(self, app):
        """Test that required signals exist."""
        thread = ExecutorThread([])
        
        # These should exist and be proper Qt signals
        assert hasattr(thread, 'entry_started')
        assert hasattr(thread, 'finished')
        
    def test_inherits_from_qthread(self, app):
        """Test that ExecutorThread inherits from QThread."""
        thread = ExecutorThread([])
        assert isinstance(thread, QThread)

    @patch('demoscene_playlist_tool.ui.executor_thread.Executor')
    def test_run_emits_finished_when_executor_raises(self, mock_executor_class, app):
        """Unexpected executor errors should still emit finished and playback_error."""
        mock_executor = MagicMock()
        mock_executor.run.side_effect = RuntimeError("boom")
        mock_executor_class.return_value = mock_executor

        thread = ExecutorThread([Path('/demo1.exe')])
        with patch.object(thread, 'finished') as mock_finished, patch.object(thread, 'playback_error') as mock_error:
            thread.run()

        mock_error.emit.assert_called_once()
        mock_finished.emit.assert_called_once()