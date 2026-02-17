"""
Export service for podcast platforms
"""
import zipfile
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import os

from app.services.rss import RSSGenerator
from app.models import Podcast, PodcastEpisode


class ExportService:
    """Service for exporting podcasts to various platforms"""
    
    def __init__(self):
        self.rss_generator = RSSGenerator()
    
    async def export_to_spotify(
        self,
        podcast: Podcast,
        episodes: List[PodcastEpisode],
        export_dir: str = "exports"
    ) -> Dict[str, Any]:
        """
        Export podcast for Spotify
        
        Args:
            podcast: Podcast model instance
            episodes: List of podcast episodes
            export_dir: Directory to save export files
            
        Returns:
            Export information dictionary
        """
        # Create export directory
        Path(export_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate RSS feed
        rss_content = self.rss_generator.generate_podcast_feed(podcast, episodes)
        
        # Save RSS file
        rss_filename = f"spotify_{podcast.id}.xml"
        rss_path = os.path.join(export_dir, rss_filename)
        with open(rss_path, "w", encoding="utf-8") as f:
            f.write(rss_content)
        
        # Create metadata JSON
        metadata = {
            "podcast_id": podcast.id,
            "title": podcast.title,
            "description": podcast.description,
            "author": podcast.user.email if podcast.user else "Unknown",
            "category": podcast.style.value,
            "language": "en",
            "rss_url": rss_path,
            "exported_at": datetime.utcnow().isoformat(),
            "episode_count": len(episodes)
        }
        
        metadata_filename = f"spotify_{podcast.id}_metadata.json"
        metadata_path = os.path.join(export_dir, metadata_filename)
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "rss_file": rss_path,
            "metadata_file": metadata_path,
            "format": "spotify",
            "episode_count": len(episodes)
        }
    
    async def export_to_apple_podcasts(
        self,
        podcast: Podcast,
        episodes: List[PodcastEpisode],
        export_dir: str = "exports"
    ) -> Dict[str, Any]:
        """
        Export podcast for Apple Podcasts
        
        Args:
            podcast: Podcast model instance
            episodes: List of podcast episodes
            export_dir: Directory to save export files
            
        Returns:
            Export information dictionary
        """
        # Create export directory
        Path(export_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate RSS feed with Apple Podcasts specific elements
        rss_content = self.rss_generator.generate_podcast_feed(podcast, episodes)
        
        # Save RSS file
        rss_filename = f"apple_{podcast.id}.xml"
        rss_path = os.path.join(export_dir, rss_filename)
        with open(rss_path, "w", encoding="utf-8") as f:
            f.write(rss_content)
        
        # Create metadata JSON
        metadata = {
            "podcast_id": podcast.id,
            "title": podcast.title,
            "description": podcast.description,
            "author": podcast.user.email if podcast.user else "Unknown",
            "category": podcast.style.value,
            "language": "en",
            "rss_url": rss_path,
            "exported_at": datetime.utcnow().isoformat(),
            "episode_count": len(episodes),
            "platform": "apple"
        }
        
        metadata_filename = f"apple_{podcast.id}_metadata.json"
        metadata_path = os.path.join(export_dir, metadata_filename)
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "rss_file": rss_path,
            "metadata_file": metadata_path,
            "format": "apple_podcasts",
            "episode_count": len(episodes)
        }
    
    async def export_to_zip(
        self,
        podcast: Podcast,
        episodes: List[PodcastEpisode],
        export_dir: str = "exports"
    ) -> Dict[str, Any]:
        """
        Export podcast as ZIP archive with all files
        
        Args:
            podcast: Podcast model instance
            episodes: List of podcast episodes
            export_dir: Directory to save export files
            
        Returns:
            Export information dictionary
        """
        # Create export directory
        Path(export_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate RSS feed
        rss_content = self.rss_generator.generate_podcast_feed(podcast, episodes)
        
        # Create temporary directory for export
        temp_dir = os.path.join(export_dir, f"export_{podcast.id}")
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        
        # Save RSS file
        rss_filename = f"{podcast.id}.xml"
        rss_path = os.path.join(temp_dir, rss_filename)
        with open(rss_path, "w", encoding="utf-8") as f:
            f.write(rss_content)
        
        # Save episode audio files (simulated)
        for i, episode in enumerate(episodes):
            audio_filename = f"episode_{i+1}.mp3"
            audio_path = os.path.join(temp_dir, audio_filename)
            # In real implementation, this would be actual audio file
            with open(audio_path, "w") as f:
                f.write(f"Audio file for episode {i+1}")
        
        # Create ZIP archive
        zip_filename = f"podcast_{podcast.id}.zip"
        zip_path = os.path.join(export_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # Add RSS file
            zipf.write(rss_path, rss_filename)
            
            # Add episode audio files
            for i, episode in enumerate(episodes):
                audio_filename = f"episode_{i+1}.mp3"
                audio_path = os.path.join(temp_dir, audio_filename)
                zipf.write(audio_path, audio_filename)
        
        # Cleanup temporary directory
        import shutil
        shutil.rmtree(temp_dir)
        
        return {
            "success": True,
            "zip_file": zip_path,
            "format": "zip",
            "episode_count": len(episodes)
        }
    
    async def generate_platform_specific_files(
        self,
        podcast: Podcast,
        episodes: List[PodcastEpisode],
        platforms: List[str],
        export_dir: str = "exports"
    ) -> Dict[str, Any]:
        """
        Generate files for multiple platforms
        
        Args:
            podcast: Podcast model instance
            episodes: List of podcast episodes
            platforms: List of platforms to export to
            export_dir: Directory to save export files
            
        Returns:
            Dictionary with export results for each platform
        """
        results = {}
        
        for platform in platforms:
            if platform.lower() == "spotify":
                results[platform] = await self.export_to_spotify(podcast, episodes, export_dir)
            elif platform.lower() == "apple":
                results[platform] = await self.export_to_apple_podcasts(podcast, episodes, export_dir)
            elif platform.lower() == "zip":
                results[platform] = await self.export_to_zip(podcast, episodes, export_dir)
            else:
                results[platform] = {
                    "success": False,
                    "error": f"Unsupported platform: {platform}"
                }
        
        return results
