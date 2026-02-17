"""
RSS feed generator for podcast platform
"""
import uuid
from datetime import datetime
from typing import List, Optional
from feedgen.feed import FeedGenerator
from feedgen.entry import FeedEntry

from app.models import Podcast, PodcastEpisode


class RSSGenerator:
    """Service for generating RSS feeds for podcasts"""
    
    def __init__(self):
        self.namespace = "http://www.itunes.com/dtds/podcast-1.0.dtd"
    
    def generate_podcast_feed(
        self,
        podcast: Podcast,
        episodes: List[PodcastEpisode],
        base_url: str = "https://api.example.com"
    ) -> str:
        """
        Generate RSS feed for a podcast
        
        Args:
            podcast: Podcast model instance
            episodes: List of podcast episodes
            base_url: Base URL for the API
            
        Returns:
            RSS feed as XML string
        """
        fg = FeedGenerator()
        
        # Basic podcast information
        fg.id(podcast.id)
        fg.title(podcast.title)
        fg.description(podcast.description or "")
        fg.author(podcast.user.email if podcast.user else "Unknown")
        fg.link(href=f"{base_url}/podcast/{podcast.id}", rel="alternate")
        fg.language("en-US")
        fg.pubDate(podcast.created_at)
        fg.lastBuildDate(datetime.utcnow())
        
        # iTunes specific information
        fg.itunes_author(podcast.user.email if podcast.user else "Unknown")
        fg.itunes_summary(podcast.description or "")
        fg.itunes_owner("Unknown", "unknown@example.com")
        fg.itunes_category("Technology", "Podcasting")
        fg.itunes_explicit("no")
        
        # Add cover image if available
        if podcast.cover_image:
            fg.itunes_image(f"{base_url}{podcast.cover_image}")
        
        # Add episodes
        for episode in episodes:
            fe = fg.add_entry()
            fe.id(episode.id)
            fe.title(episode.title)
            fe.description(episode.description or "")
            fe.pubDate(episode.published_at or episode.created_at)
            
            # Audio file
            if episode.audio_file:
                fe.enclosure(
                    url=f"{base_url}{episode.audio_file}",
                    length=str(episode.duration_seconds or 0),
                    type="audio/mpeg"
                )
            
            # iTunes specific episode information
            fe.itunes_summary(episode.description or "")
            fe.itunes_duration(str(episode.duration_seconds or 0))
            fe.itunes_explicit("no")
            
            # Episode number
            fe.itunes_episode(episode.episode_number)
        
        return fg.rss_str()
    
    def generate_simple_feed(
        self,
        title: str,
        description: str,
        episodes: List[dict],
        base_url: str = "https://api.example.com"
    ) -> str:
        """
        Generate a simple RSS feed
        
        Args:
            title: Feed title
            description: Feed description
            episodes: List of episode dictionaries
            base_url: Base URL for the API
            
        Returns:
            RSS feed as XML string
        """
        fg = FeedGenerator()
        
        # Basic feed information
        fg.id(str(uuid.uuid4()))
        fg.title(title)
        fg.description(description)
        fg.link(href=base_url, rel="alternate")
        fg.language("en-US")
        fg.pubDate(datetime.utcnow())
        fg.lastBuildDate(datetime.utcnow())
        
        # Add episodes
        for episode_data in episodes:
            fe = fg.add_entry()
            fe.id(episode_data.get("id", str(uuid.uuid4())))
            fe.title(episode_data.get("title", ""))
            fe.description(episode_data.get("description", ""))
            fe.pubDate(episode_data.get("pub_date", datetime.utcnow()))
            
            # Audio file
            audio_file = episode_data.get("audio_file")
            if audio_file:
                fe.enclosure(
                    url=f"{base_url}{audio_file}",
                    length=str(episode_data.get("duration", 0)),
                    type="audio/mpeg"
                )
        
        return fg.rss_str()
    
    def validate_feed(self, rss_xml: str) -> bool:
        """
        Validate RSS feed structure
        
        Args:
            rss_xml: RSS feed XML string
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic validation - check if it starts with XML declaration
            if not rss_xml.strip().startswith("<?xml"):
                return False
            
            # More sophisticated validation would use an XML parser
            # For now, we'll just check basic structure
            return True
        except Exception:
            return False
