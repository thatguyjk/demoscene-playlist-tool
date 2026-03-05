"""Integration tests for recent changes and edge cases."""
import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from PyQt6.QtWidgets import QApplication
from demoscene_playlist_tool.ui.main_window import MainWindow
from demoscene_playlist_tool.core.playlist import Playlist, PlaylistEntry


@pytest.fixture
def app():
    """Create QApplication instance for testing UI components."""
    return QApplication.instance() or QApplication([])


@pytest.fixture  
def main_window(app):
    """Create a MainWindow instance for testing."""
    return MainWindow()


class TestRecentChangesIntegration:
    """Integration tests for the recently added selected entry functionality."""
    
    @patch('demoscene_playlist_tool.ui.main_window.QFileDialog.getOpenFileName')
    @patch('demoscene_playlist_tool.ui.main_window.ExecutorThread')
    def test_full_workflow_add_select_play(self, mock_thread_class, mock_dialog, main_window):
        """Test complete workflow: add entries, select one, then play from selection."""
        mock_thread = MagicMock()
        mock_thread_class.return_value = mock_thread
        
        # Add multiple entries
        mock_dialog.side_effect = [
            ("/demo1.exe", ""),
            ("/demo2.exe", ""), 
            ("/demo3.exe", "")
        ]
        
        main_window._add_entry()  # Add first - should set selected to 0
        main_window._add_entry()  # Add second
        main_window._add_entry()  # Add third
        
        assert main_window._selected_entry == 0
        assert len(main_window._playlist) == 3
        
        # Select second entry (index 1)
        main_window._list.setCurrentRow(1)
        main_window._set_selected()
        assert main_window._selected_entry == 1
        
        # Play from selected entry
        main_window._play()
        
        # Verify ExecutorThread was created correctly and start index was set
        expected_paths = [Path("/demo1.exe"), Path("/demo2.exe"), Path("/demo3.exe")]
        mock_thread_class.assert_called_once_with(expected_paths)
        mock_thread.set_start_index.assert_called_once_with(1)
        mock_thread.start.assert_called_once()
        
    @patch('demoscene_playlist_tool.ui.main_window.QFileDialog.getOpenFileName')
    def test_playlist_manipulation_preserves_selection_logic(self, mock_dialog, main_window):
        """Test that playlist operations work correctly with selection tracking."""
        # Add entries
        mock_dialog.side_effect = [("/first.exe", ""), ("/second.exe", ""), ("/third.exe", "")]
        
        main_window._add_entry()  # selected_entry becomes 0
        main_window._add_entry()  # selected_entry stays 0  
        main_window._add_entry()  # selected_entry stays 0
        
        assert main_window._selected_entry == 0
        
        # Select middle entry and track it
        main_window._list.setCurrentRow(1) 
        main_window._set_selected()
        assert main_window._selected_entry == 1
        
        # Move the selected entry up - UI should account for this
        main_window._list.setCurrentRow(1)  # Re-select item at position 1
        main_window._move_up()
        
        # The entry that was at position 1 is now at position 0
        assert main_window._list.currentRow() == 0
        assert main_window._playlist.entries[0].path == Path("/second.exe")
        
    def test_selected_entry_tracking_edge_cases(self, main_window):
        """Test edge cases for selected entry tracking."""
        # No entries - selected should be None
        assert main_window._selected_entry is None
        
        # Add one entry - selected should become 0
        main_window._playlist.add(Path("/test.exe"))
        main_window._list.addItem("/test.exe")
        if main_window._selected_entry is None:
            main_window._selected_entry = 0
            
        assert main_window._selected_entry == 0
        
        # Remove the only entry
        main_window._list.setCurrentRow(0)
        main_window._remove_entry()
        
        assert len(main_window._playlist) == 0
        assert main_window._list.count() == 0
        # selected_entry behavior after removal is implementation-dependent
        
    def test_set_selected_with_no_selection(self, main_window):
        """Test _set_selected when no item is selected in list."""
        main_window._playlist.add(Path("/test.exe"))
        main_window._list.addItem("/test.exe")
        main_window._list.setCurrentRow(-1)  # No selection
        
        main_window._set_selected()
        
        # Should handle -1 (no selection) appropriately
        assert main_window._selected_entry == -1


class TestPlaylistSaveLoadWithPaths:
    """Test playlist save/load functionality with actual path objects."""
    
    def test_save_load_preserves_path_objects(self, tmp_path):
        """Test that save/load cycle preserves Path objects correctly."""
        playlist = Playlist()
        
        # Add Path objects
        playlist.add(Path("/absolute/path/demo1.exe"))
        playlist.add(Path("relative/demo2.exe"))
        playlist.add(Path("C:\\Windows\\demo3.exe"))  # Windows path
        
        # Save
        save_file = tmp_path / "test_playlist.json"
        playlist.save(save_file)
        
        # Verify file content - use str() to get platform-appropriate paths
        saved_data = json.loads(save_file.read_text(encoding="utf-8"))
        expected_entries = [
            str(Path("/absolute/path/demo1.exe")),
            str(Path("relative/demo2.exe")), 
            str(Path("C:\\Windows\\demo3.exe"))
        ]
        assert saved_data["entries"] == expected_entries
        
        # Load
        loaded_playlist = Playlist.load(save_file)
        
        # Verify loaded paths - compare the actual Path objects
        assert len(loaded_playlist) == 3
        assert loaded_playlist.entries[0].path == Path("/absolute/path/demo1.exe")
        assert loaded_playlist.entries[1].path == Path("relative/demo2.exe") 
        assert loaded_playlist.entries[2].path == Path("C:\\Windows\\demo3.exe")
        
    def test_playlist_entry_exists_functionality(self, tmp_path):
        """Test the PlaylistEntry.exists() method."""
        # Create a real file
        real_file = tmp_path / "real_demo.exe"
        real_file.touch()
        
        # Create entries
        existing_entry = PlaylistEntry(path=real_file)
        missing_entry = PlaylistEntry(path=tmp_path / "missing_demo.exe")
        
        assert existing_entry.exists() is True
        assert missing_entry.exists() is False


class TestErrorHandling:
    """Test error handling in recent changes."""
    
    def test_play_with_invalid_selected_index(self, app):
        """Test play functionality when selected_entry is invalid."""
        with patch('demoscene_playlist_tool.ui.main_window.ExecutorThread') as mock_thread_class:
            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread
            
            main_window = MainWindow()
            
            # Add entries
            main_window._playlist.add(Path("/demo1.exe")) 
            main_window._playlist.add(Path("/demo2.exe"))
            
            # Set invalid selected entry
            main_window._selected_entry = 10  # Out of range
            
            main_window._play()
            
            # Should still work, ExecutorThread should handle invalid index
            mock_thread_class.assert_called_once()
            mock_thread.set_start_index.assert_called_once_with(10)
            mock_thread.start.assert_called_once()
            
    def test_move_operations_edge_cases(self, main_window):
        """Test move operations with edge cases."""
        # Try moving with empty playlist
        main_window._move_up()  # Should not crash
        main_window._move_down()  # Should not crash
        
        # Add single entry
        main_window._playlist.add(Path("/single.exe"))
        main_window._list.addItem("/single.exe")
        main_window._list.setCurrentRow(0)
        
        # Try moving single entry
        main_window._move_up()    # Should do nothing
        main_window._move_down()  # Should do nothing
        
        assert len(main_window._playlist) == 1
        assert main_window._playlist.entries[0].path == Path("/single.exe")
        
    def test_operations_with_no_list_selection(self, main_window):
        """Test operations when list has no current selection."""
        # Add entries but don't select any
        main_window._playlist.add(Path("/demo1.exe"))
        main_window._playlist.add(Path("/demo2.exe"))
        main_window._list.addItem("/demo1.exe")
        main_window._list.addItem("/demo2.exe")
        main_window._list.setCurrentRow(-1)  # No selection
        
        # Operations should handle no selection gracefully
        original_count = len(main_window._playlist)
        
        main_window._remove_entry()  # Should do nothing
        main_window._move_up()       # Should do nothing  
        main_window._move_down()     # Should do nothing
        
        assert len(main_window._playlist) == original_count