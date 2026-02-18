// API Types for AI Podcast Platform

export interface Podcast {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  style: 'academic' | 'entertainment' | 'business';
  num_participants: number;
  status: PodcastStatus;
  source_type: 'pdf' | 'docx' | 'url' | 'text';
  source_file?: string;
  source_url?: string;
  extracted_text?: string;
  scenario?: string;
  audio_file?: string;
  cover_image?: string;
  rss_feed?: string;
  duration_seconds?: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export type PodcastStatus =
  | 'pending'
  | 'extracting_text'
  | 'generating_scenario'
  | 'synthesizing_speech'
  | 'processing_audio'
  | 'generating_cover'
  | 'completed'
  | 'failed';

export interface PodcastParticipant {
  id: string;
  podcast_id: string;
  name: string;
  role: 'host' | 'expert' | 'commentator' | 'guest';
  voice_provider: string;
  voice_id: string;
  voice_settings?: Record<string, unknown>;
}

export interface PodcastCreate {
  title: string;
  description?: string;
  style: 'academic' | 'entertainment' | 'business';
  num_participants: number;
  source_type: 'pdf' | 'docx' | 'url' | 'text';
  source_url?: string;
  source_text?: string;
  participants: ParticipantCreate[];
}

export interface ParticipantCreate {
  name: string;
  role: 'host' | 'expert' | 'commentator' | 'guest';
  voice_provider: string;
  voice_id: string;
  voice_settings?: Record<string, unknown>;
}

export interface PodcastUpdate {
  title?: string;
  description?: string;
  style?: 'academic' | 'entertainment' | 'business';
}

export interface ProgressResponse {
  podcast_id: string;
  status: PodcastStatus;
  progress_percent: number;
  current_step: string;
  error_message?: string;
  estimated_time_remaining_seconds?: number;
}

export interface Voice {
  id: string;
  name: string;
  provider: string;
  gender: 'male' | 'female' | 'neutral';
  language: string;
  description?: string;
  preview_url?: string;
}

export interface TextExtractionResult {
  text: string;
  source_type: string;
  error?: string;
}

export interface ScenarioGenerationResult {
  title: string;
  description: string;
  dialogue: DialogueLine[];
  total_lines: number;
  estimated_duration_minutes: number;
  error?: string;
}

export interface DialogueLine {
  participant: string;
  role: string;
  text: string;
}
