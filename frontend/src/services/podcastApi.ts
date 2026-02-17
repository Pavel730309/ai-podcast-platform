import apiClient from './api';
import type { Podcast, PodcastCreate, PodcastUpdate, ProgressResponse } from '../types/api';

export const podcastApi = {
  // Get all podcasts
  getPodcasts: async (skip = 0, limit = 20): Promise<Podcast[]> => {
    const response = await apiClient.get('/podcasts', { params: { skip, limit } });
    return response.data;
  },

  // Get single podcast
  getPodcast: async (id: string): Promise<Podcast> => {
    const response = await apiClient.get(`/podcasts/${id}`);
    return response.data;
  },

  // Create new podcast
  createPodcast: async (data: PodcastCreate): Promise<Podcast> => {
    const response = await apiClient.post('/podcasts', data);
    return response.data;
  },

  // Update podcast
  updatePodcast: async (id: string, data: PodcastUpdate): Promise<Podcast> => {
    const response = await apiClient.patch(`/podcasts/${id}`, data);
    return response.data;
  },

  // Delete podcast
  deletePodcast: async (id: string): Promise<void> => {
    await apiClient.delete(`/podcasts/${id}`);
  },

  // Get podcast progress
  getProgress: async (id: string): Promise<ProgressResponse> => {
    const response = await apiClient.get(`/podcasts/${id}/progress`);
    return response.data;
  },
};
