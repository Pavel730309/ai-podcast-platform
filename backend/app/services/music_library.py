"""
Music library service for background tracks
"""

import json
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class MusicTrack:
    """Music track model"""

    id: str
    name: str
    category: str  # instrumental, electronic, ambient, corporate
    mood: str  # relaxing, energetic, neutral, upbeat
    file_path: str
    duration_seconds: int
    bpm: int
    license_info: str


class MusicLibrary:
    """Service for managing background music library"""

    def __init__(self, music_dir: str = "data/music"):
        self.music_dir = Path(music_dir)
        self._tracks: List[MusicTrack] = []
        self._load_tracks()

    def _load_tracks(self):
        """Load tracks from metadata file or create defaults"""
        metadata_file = self.music_dir / "metadata.json"

        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                data = json.load(f)
                self._tracks = [MusicTrack(**track) for track in data]
        else:
            # Create default metadata
            self._tracks = self._get_default_tracks()
            self._save_metadata()

    def _save_metadata(self):
        """Save tracks metadata to file"""
        metadata_file = self.music_dir / "metadata.json"
        data = [
            {
                "id": track.id,
                "name": track.name,
                "category": track.category,
                "mood": track.mood,
                "file_path": track.file_path,
                "duration_seconds": track.duration_seconds,
                "bpm": track.bpm,
                "license_info": track.license_info,
            }
            for track in self._tracks
        ]
        with open(metadata_file, "w") as f:
            json.dump(data, f, indent=2)

    def _get_default_tracks(self) -> List[MusicTrack]:
        """Get default royalty-free tracks metadata"""
        return [
            # Instrumental
            MusicTrack(
                id="inst_001",
                name="Calm Acoustic",
                category="instrumental",
                mood="relaxing",
                file_path="data/music/instrumental/calm_acoustic.mp3",
                duration_seconds=180,
                bpm=80,
                license_info="Royalty-free - Pixabay",
            ),
            MusicTrack(
                id="inst_002",
                name="Piano Reflections",
                category="instrumental",
                mood="relaxing",
                file_path="data/music/instrumental/piano_reflections.mp3",
                duration_seconds=240,
                bpm=70,
                license_info="Royalty-free - Pixabay",
            ),
            MusicTrack(
                id="inst_003",
                name="Upbeat Guitar",
                category="instrumental",
                mood="energetic",
                file_path="data/music/instrumental/upbeat_guitar.mp3",
                duration_seconds=200,
                bpm=120,
                license_info="Royalty-free - Pixabay",
            ),
            # Electronic
            MusicTrack(
                id="elec_001",
                name="Tech Background",
                category="electronic",
                mood="neutral",
                file_path="data/music/electronic/tech_background.mp3",
                duration_seconds=300,
                bpm=110,
                license_info="Royalty-free - Pixabay",
            ),
            MusicTrack(
                id="elec_002",
                name="Future Bass",
                category="electronic",
                mood="energetic",
                file_path="data/music/electronic/future_bass.mp3",
                duration_seconds=240,
                bpm=140,
                license_info="Royalty-free - Pixabay",
            ),
            # Ambient
            MusicTrack(
                id="amb_001",
                name="Space Drone",
                category="ambient",
                mood="relaxing",
                file_path="data/music/ambient/space_drone.mp3",
                duration_seconds=360,
                bpm=60,
                license_info="Royalty-free - Pixabay",
            ),
            MusicTrack(
                id="amb_002",
                name="Nature Sounds",
                category="ambient",
                mood="relaxing",
                file_path="data/music/ambient/nature_sounds.mp3",
                duration_seconds=300,
                bpm=70,
                license_info="Royalty-free - Pixabay",
            ),
            # Corporate
            MusicTrack(
                id="corp_001",
                name="Business Success",
                category="corporate",
                mood="upbeat",
                file_path="data/music/corporate/business_success.mp3",
                duration_seconds=180,
                bpm=115,
                license_info="Royalty-free - Pixabay",
            ),
            MusicTrack(
                id="corp_002",
                name="Corporate Vision",
                category="corporate",
                mood="neutral",
                file_path="data/music/corporate/corporate_vision.mp3",
                duration_seconds=240,
                bpm=100,
                license_info="Royalty-free - Pixabay",
            ),
        ]

    def get_tracks(
        self,
        category: Optional[str] = None,
        mood: Optional[str] = None,
    ) -> List[MusicTrack]:
        """Get tracks with optional filtering"""
        tracks = self._tracks

        if category:
            tracks = [t for t in tracks if t.category == category]

        if mood:
            tracks = [t for t in tracks if t.mood == mood]

        return tracks

    def get_track(self, track_id: str) -> Optional[MusicTrack]:
        """Get a specific track by ID"""
        for track in self._tracks:
            if track.id == track_id:
                return track
        return None

    def get_categories(self) -> List[str]:
        """Get all available categories"""
        return list(set(t.category for t in self._tracks))

    def get_moods(self) -> List[str]:
        """Get all available moods"""
        return list(set(t.mood for t in self._tracks))

    def suggest_track(
        self,
        podcast_style: str,
        duration_seconds: Optional[int] = None,
    ) -> Optional[MusicTrack]:
        """Suggest a track based on podcast style"""
        style_mapping = {
            "academic": ("ambient", "relaxing"),
            "entertainment": ("electronic", "energetic"),
            "business": ("corporate", "neutral"),
        }

        category, mood = style_mapping.get(podcast_style, ("instrumental", "neutral"))

        tracks = self.get_tracks(category=category, mood=mood)

        if tracks:
            # If duration specified, find track that can loop reasonably
            if duration_seconds:
                tracks = [t for t in tracks if t.duration_seconds >= 60]

            # Return first matching track
            return tracks[0] if tracks else None

        # Fallback to any track
        return self._tracks[0] if self._tracks else None

    def get_track_file(self, track_id: str) -> Optional[Path]:
        """Get the file path for a track"""
        track = self.get_track(track_id)
        if track:
            path = Path(track.file_path)
            if path.exists():
                return path
        return None


# Global instance
music_library = MusicLibrary()
