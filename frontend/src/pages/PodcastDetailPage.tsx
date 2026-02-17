import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Play, Pause, Download, Clock, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import toast from 'react-hot-toast';
import { podcastApi } from '../services/podcastApi';
import type { Podcast, ProgressResponse } from '../types/api';

const PodcastDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const [podcast, setPodcast] = useState<Podcast | null>(null);
  const [progress, setProgress] = useState<ProgressResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (id) {
      fetchPodcast();
    }
  }, [id]);

  useEffect(() => {
    // Poll for progress if podcast is not completed
    if (podcast && podcast.status !== 'completed' && podcast.status !== 'failed') {
      const interval = setInterval(fetchProgress, 5000);
      return () => clearInterval(interval);
    }
  }, [podcast?.status]);

  const fetchPodcast = async () => {
    try {
      setIsLoading(true);
      const data = await podcastApi.getPodcast(id!);
      setPodcast(data);
      
      // Also fetch progress
      if (data.status !== 'completed' && data.status !== 'failed') {
        fetchProgress();
      }
    } catch (error) {
      toast.error('Failed to load podcast');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchProgress = async () => {
    try {
      const progressData = await podcastApi.getProgress(id!);
      setProgress(progressData);
    } catch (error) {
      console.error('Failed to fetch progress:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-6 w-6 text-red-500" />;
      case 'pending':
        return <Clock className="h-6 w-6 text-gray-400" />;
      default:
        return <Loader className="h-6 w-6 text-primary-500 animate-spin" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      case 'pending':
        return 'Pending';
      case 'extracting_text':
        return 'Extracting Text';
      case 'generating_scenario':
        return 'Generating Scenario';
      case 'synthesizing_speech':
        return 'Synthesizing Speech';
      case 'processing_audio':
        return 'Processing Audio';
      case 'generating_cover':
        return 'Generating Cover';
      default:
        return status;
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (!podcast) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Podcast not found</h2>
        <Link to="/podcasts" className="text-primary-600 hover:text-primary-700">
          ← Back to My Podcasts
        </Link>
      </div>
    );
  }

  const currentProgress = progress?.progress_percent || 0;
  const isProcessing = podcast.status !== 'completed' && podcast.status !== 'failed';

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <Link 
          to="/podcasts" 
          className="text-primary-600 hover:text-primary-700 font-medium mb-4 inline-block"
        >
          ← Back to My Podcasts
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{podcast.title}</h1>
        <div className="flex items-center space-x-4 text-sm text-gray-600">
          <span className="flex items-center">
            {getStatusIcon(podcast.status)}
            <span className="ml-2">{getStatusText(podcast.status)}</span>
          </span>
          {podcast.duration_seconds && (
            <span className="flex items-center">
              <Clock className="h-4 w-4 mr-1" />
              {Math.floor(podcast.duration_seconds / 60)}:{(podcast.duration_seconds % 60).toString().padStart(2, '0')}
            </span>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      {isProcessing && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              {progress?.current_step || 'Processing...'}
            </span>
            <span className="text-sm text-gray-500">{currentProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              className="bg-primary-600 h-2.5 rounded-full transition-all duration-500"
              style={{ width: `${currentProgress}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {podcast.status === 'failed' && podcast.error_message && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-6">
          <div className="flex items-start">
            <AlertCircle className="h-5 w-5 text-red-500 mr-3 mt-0.5" />
            <div>
              <h3 className="text-red-800 font-medium">Generation Failed</h3>
              <p className="text-red-700 mt-1">{podcast.error_message}</p>
            </div>
          </div>
        </div>
      )}

      {/* Audio Player */}
      {podcast.status === 'completed' && podcast.audio_file && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Listen</h2>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="bg-primary-600 text-white rounded-full p-4 hover:bg-primary-700 transition-colors"
            >
              {isPlaying ? (
                <Pause className="h-6 w-6" />
              ) : (
                <Play className="h-6 w-6" />
              )}
            </button>
            <div className="flex-1">
              <div className="bg-gray-200 rounded-full h-2">
                <div className="bg-primary-600 h-2 rounded-full w-0"></div>
              </div>
            </div>
            <a
              href={podcast.audio_file}
              download
              className="flex items-center text-primary-600 hover:text-primary-700"
            >
              <Download className="h-5 w-5 mr-1" />
              Download
            </a>
          </div>
        </div>
      )}

      {/* Cover Image */}
      {podcast.cover_image && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Cover</h2>
          <img 
            src={podcast.cover_image} 
            alt={podcast.title}
            className="w-64 h-64 object-cover rounded-lg shadow-md"
          />
        </div>
      )}

      {/* Details */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Details</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Style</p>
            <p className="font-medium">{podcast.style}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Participants</p>
            <p className="font-medium">{podcast.num_participants}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Source Type</p>
            <p className="font-medium">{podcast.source_type}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Created</p>
            <p className="font-medium">{new Date(podcast.created_at).toLocaleDateString()}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PodcastDetailPage;
