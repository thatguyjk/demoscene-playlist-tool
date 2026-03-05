"""Tests for the MainWindow UI component."""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

from demoscene_playlist_tool.ui.main_window import MainWindow


@pytest.fixture
def app():
    """Create QApplication instance for testing UI components."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def main_window(app):
    """Create a MainWindow instance for testing."""
    window = MainWindow()
    return window


class TestMainWindow:
    """Test MainWindow functionality."""
    
    def test_window_initialization(self, main_window):
        """Test that window initializes with correct title and size."""
        assert main_window.windowTitle() == "Demoscene Playlist Tool"
        assert main_window.size().width() == 600
        assert main_window.size().height() == 400
        assert main_window._selected_entry is None
        assert len(main_window._playlist) == 0
        
    def test_playlist_starts_empty(self, main_window):
        """Test that playlist starts empty."""
        assert len(main_window._playlist) == 0
        assert main_window._list.count() == 0
        
    @patch('demoscene_playlist_tool.ui.main_window.QFileDialog.getOpenFileName')
    def test_add_entry_with_file_selected(self, mock_dialog, main_window):
        """Test adding entry when file is selected in dialog."""
        mock_dialog.return_value = ("/fake/demo.exe", "")
        
        main_window._add_entry()
        
        assert len(main_window._playlist) == 1
        assert main_window._list.count() == 1
        assert main_window._selected_entry == 0  # First entry should set selected to 0
        assert main_window._list.item(0).text() == "/fake/demo.exe"
        
    @patch('demoscene_playlist_tool.ui.main_window.QFileDialog.getOpenFileName')
    def test_add_entry_dialog_cancelled(self, mock_dialog, main_window):
        """Test adding entry when dialog is cancelled."""
        mock_dialog.return_value = ("", "")
        
        main_window._add_entry()
        
        assert len(main_window._playlist) == 0
        assert main_window._list.count() == 0
        assert main_window._selected_entry is None
        
    @patch('demoscene_playlist_tool.ui.main_window.QFileDialog.getOpenFileName')
    def test_add_multiple_entries_preserves_selection(self, mock_dialog, main_window):
        """Test that adding multiple entries doesn't change selected_entry after first."""
        mock_dialog.side_effect = [("/first.exe", ""), ("/second.exe", "")]
        
        main_window._add_entry()  # First entry
        assert main_window._selected_entry == 0
        
        main_window._add_entry()  # Second entry
        assert main_window._selected_entry == 0  # Should still be 0
        assert len(main_window._playlist) == 2
        
    def test_remove_entry_with_selection(self, main_window):
        """Test removing entry when one is selected."""
        # Add test entries
        main_window._playlist.add(Path("/first.exe"))
        main_window._playlist.add(Path("/second.exe"))
        main_window._list.addItem("/first.exe")
        main_window._list.addItem("/second.exe")
        
        # Select first item
        main_window._list.setCurrentRow(0)
        
        main_window._remove_entry()
        
        assert len(main_window._playlist) == 1
        assert main_window._list.count() == 1
        assert main_window._playlist.entries[0].path == Path("/second.exe")
        
    def test_remove_entry_no_selection(self, main_window):
        """Test removing entry when nothing is selected."""
        main_window._playlist.add(Path("/test.exe"))
        main_window._list.addItem("/test.exe") 
        main_window._list.setCurrentRow(-1)  # No selection
        
        main_window._remove_entry()
        
        # Nothing should be removed
        assert len(main_window._playlist) == 1
        assert main_window._list.count() == 1
        
    def test_move_up_from_second_position(self, main_window):
        """Test moving entry up from second position."""
        # Add test entries
        main_window._playlist.add(Path("/first.exe"))
        main_window._playlist.add(Path("/second.exe"))
        main_window._list.addItem("/first.exe")
        main_window._list.addItem("/second.exe")
        
        # Select second item
        main_window._list.setCurrentRow(1)
        
        main_window._move_up()
        
        assert main_window._playlist.entries[0].path == Path("/second.exe")
        assert main_window._playlist.entries[1].path == Path("/first.exe")
        assert main_window._list.currentRow() == 0
        
    def test_move_up_from_first_position(self, main_window):
        """Test moving up from first position does nothing."""
        main_window._playlist.add(Path("/test.exe"))
        main_window._list.addItem("/test.exe")
        main_window._list.setCurrentRow(0)
        
        main_window._move_up()
        
        # Nothing should change
        assert main_window._playlist.entries[0].path == Path("/test.exe")
        assert main_window._list.currentRow() == 0
        
    def test_move_down_from_first_position(self, main_window):
        """Test moving entry down from first position."""
        # Add test entries
        main_window._playlist.add(Path("/first.exe"))
        main_window._playlist.add(Path("/second.exe"))
        main_window._list.addItem("/first.exe")
        main_window._list.addItem("/second.exe")
        
        # Select first item
        main_window._list.setCurrentRow(0)
        
        main_window._move_down()
        
        assert main_window._playlist.entries[0].path == Path("/second.exe")
        assert main_window._playlist.entries[1].path == Path("/first.exe")
        assert main_window._list.currentRow() == 1
        
    def test_move_down_from_last_position(self, main_window):
        """Test moving down from last position does nothing."""
        main_window._playlist.add(Path("/test.exe"))
        main_window._list.addItem("/test.exe")
        main_window._list.setCurrentRow(0)
        
        main_window._move_down()
        
        # Nothing should change (only one item)
        assert main_window._playlist.entries[0].path == Path("/test.exe")
        assert main_window._list.currentRow() == 0
        
    def test_set_selected_entry(self, main_window):
        """Test _set_selected method updates selected_entry."""
        # Add entries and set selection
        main_window._playlist.add(Path("/first.exe"))
        main_window._playlist.add(Path("/second.exe"))
        main_window._list.addItem("/first.exe")
        main_window._list.addItem("/second.exe")
        main_window._list.setCurrentRow(1)
        
        main_window._set_selected()
        
        assert main_window._selected_entry == 1
        
    @patch('demoscene_playlist_tool.ui.main_window.QFileDialog.getOpenFileName')
    def test_open_playlist_file_selected(self, mock_dialog, main_window, tmp_path):
        """Test opening playlist when file is selected."""
        # Create test playlist file
        playlist_file = tmp_path / "test.json"
        playlist_content = {
            "entries": ["/demo1.exe", "/demo2.exe"]
        }
        playlist_file.write_text(f'{playlist_content}'.replace("'", '"'))
        
        mock_dialog.return_value = (str(playlist_file), "")
        
        main_window._open_playlist()
        
        assert len(main_window._playlist) == 2
        assert main_window._list.count() == 2
        assert main_window._playlist.entries[0].path == Path("/demo1.exe")
        assert main_window._playlist.entries[1].path == Path("/demo2.exe")
        
    @patch('demoscene_playlist_tool.ui.main_window.QFileDialog.getOpenFileName') 
    def test_open_playlist_cancelled(self, mock_dialog, main_window):
        """Test opening playlist when dialog is cancelled."""
        mock_dialog.return_value = ("", "")
        
        original_count = len(main_window._playlist)
        main_window._open_playlist()
        
        assert len(main_window._playlist) == original_count
        
    @patch('demoscene_playlist_tool.ui.main_window.QFileDialog.getSaveFileName')
    def test_save_playlist_file_selected(self, mock_dialog, main_window, tmp_path):
        """Test saving playlist when file is selected."""
        # Add entries to save
        main_window._playlist.add(Path("/demo1.exe"))
        main_window._playlist.add(Path("/demo2.exe"))
        
        save_path = tmp_path / "saved_playlist.json"
        mock_dialog.return_value = (str(save_path), "")
        
        main_window._save_playlist()
        
        assert save_path.exists()
        # The actual content validation is tested in test_playlist.py
        
    @patch('demoscene_playlist_tool.ui.main_window.QFileDialog.getSaveFileName')
    def test_save_playlist_adds_json_extension(self, mock_dialog, main_window, tmp_path):
        """Test that .json extension is added if missing."""
        main_window._playlist.add(Path("/demo.exe"))
        
        save_path_no_ext = tmp_path / "playlist"
        mock_dialog.return_value = (str(save_path_no_ext), "")
        
        main_window._save_playlist()
        
        json_path = Path(str(save_path_no_ext) + ".json")
        assert json_path.exists()
        
    @patch('demoscene_playlist_tool.ui.main_window.QFileDialog.getSaveFileName')
    def test_save_playlist_cancelled(self, mock_dialog, main_window):
        """Test saving playlist when dialog is cancelled."""
        mock_dialog.return_value = ("", "")
        
        # Should not raise any errors
        main_window._save_playlist()
        
    @patch('demoscene_playlist_tool.ui.main_window.ExecutorThread')
    def test_play_with_entries_no_selection(self, mock_thread_class, main_window):
        """Test play functionality when no entry is selected."""
        mock_thread = MagicMock()
        mock_thread_class.return_value = mock_thread
        
        # Add entries
        main_window._playlist.add(Path("/demo1.exe"))
        main_window._playlist.add(Path("/demo2.exe"))
        main_window._selected_entry = None
        
        main_window._play()
        
        # Thread should be created with paths
        expected_paths = [Path("/demo1.exe"), Path("/demo2.exe")]
        mock_thread_class.assert_called_once_with(expected_paths)
        
        # set_start_index should not be called when no selection
        mock_thread.set_start_index.assert_not_called()
        
        # Thread should be started and button disabled
        mock_thread.start.assert_called_once()
        assert not main_window._play_btn.isEnabled()
        
    @patch('demoscene_playlist_tool.ui.main_window.ExecutorThread')
    def test_play_with_selected_entry(self, mock_thread_class, main_window):
        """Test play functionality starting from selected entry."""
        mock_thread = MagicMock()
        mock_thread_class.return_value = mock_thread
        
        # Add entries and set selection
        main_window._playlist.add(Path("/demo1.exe"))
        main_window._playlist.add(Path("/demo2.exe"))
        main_window._selected_entry = 1
        
        main_window._play()
        
        # Thread should be created and start index set
        expected_paths = [Path("/demo1.exe"), Path("/demo2.exe")]
        mock_thread_class.assert_called_once_with(expected_paths)
        mock_thread.set_start_index.assert_called_once_with(1)
        
        # Thread should be started and button disabled
        mock_thread.start.assert_called_once()
        assert not main_window._play_btn.isEnabled()
        
    def test_play_empty_playlist(self, main_window):
        """Test play does nothing when playlist is empty."""
        assert len(main_window._playlist) == 0
        
        main_window._play()
        
        # Play button should remain enabled
        assert main_window._play_btn.isEnabled()
        assert main_window._thread is None
        
    def test_on_playback_finished(self, main_window):
        """Test playback finished handler re-enables play button."""
        main_window._play_btn.setEnabled(False)
        
        main_window._on_playback_finished()
        
        assert main_window._play_btn.isEnabled()
        # Status should be updated (we can't easily test the exact message 
        # without accessing private QStatusBar internals)