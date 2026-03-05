from pathlib import Path

from demoscene_playlist_tool.core.playlist import Playlist, PlaylistEntry


def test_add_entry():
    p = Playlist()
    p.add(Path("/fake/demo.exe"))
    assert len(p) == 1
    assert p.entries[0].path == Path("/fake/demo.exe")


def test_remove_entry():
    p = Playlist()
    p.add(Path("/a.exe"))
    p.add(Path("/b.exe"))
    p.remove(0)
    assert len(p) == 1
    assert p.entries[0].path == Path("/b.exe")


def test_move_entry():
    p = Playlist()
    p.add(Path("/a.exe"))
    p.add(Path("/b.exe"))
    p.add(Path("/c.exe"))
    p.move(0, 2)
    assert [e.path.name for e in p.entries] == ["b.exe", "c.exe", "a.exe"]


def test_playlist_entry_exists(tmp_path):
    f = tmp_path / "demo.exe"
    f.touch()
    entry = PlaylistEntry(path=f)
    assert entry.exists()
    entry_missing = PlaylistEntry(path=tmp_path / "nope.exe")
    assert not entry_missing.exists()


def test_save_and_load(tmp_path):
    p = Playlist()
    p.add(Path("/demos/a.exe"))
    p.add(Path("/demos/b.exe"))
    dest = tmp_path / "playlist.json"
    p.save(dest)

    loaded = Playlist.load(dest)
    assert len(loaded) == 2
    assert loaded.entries[0].path == Path("/demos/a.exe")
    assert loaded.entries[1].path == Path("/demos/b.exe")


def test_load_empty_playlist(tmp_path):
    dest = tmp_path / "empty.json"
    Playlist().save(dest)
    loaded = Playlist.load(dest)
    assert len(loaded) == 0
