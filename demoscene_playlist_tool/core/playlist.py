import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PlaylistEntry:
    path: Path

    def exists(self) -> bool:
        return self.path.exists()


@dataclass
class Playlist:
    entries: list[PlaylistEntry] = field(default_factory=list)

    def add(self, path: Path) -> None:
        self.entries.append(PlaylistEntry(path=path))

    def remove(self, index: int) -> None:
        del self.entries[index]

    def move(self, index: int, new_index: int) -> None:
        entry = self.entries.pop(index)
        self.entries.insert(new_index, entry)

    def save(self, dest: Path) -> None:
        data = {"entries": [str(e.path) for e in self.entries]}
        dest.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, src: Path) -> "Playlist":
        data = json.loads(src.read_text(encoding="utf-8"))
        playlist = cls()
        for raw in data.get("entries", []):
            playlist.add(Path(raw))
        return playlist

    def __len__(self) -> int:
        return len(self.entries)
