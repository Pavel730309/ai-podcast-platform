import apiClient from './api';

export interface ExportInfo {
  type: string;
  format: string;
  url: string;
  description: string;
}

export interface ExportInfoResponse {
  podcast_id: string;
  title: string;
  available_exports: ExportInfo[];
}

export const exportApi = {
  /**
   * Get available export options for a podcast.
   */
  getExportInfo: async (podcastId: string): Promise<ExportInfoResponse> => {
    const response = await apiClient.get(`/export/podcast/${podcastId}/info`);
    return response.data;
  },

  /**
   * Download podcast audio as MP3.
   * Opens a browser download dialog.
   */
  downloadAudio: (podcastId: string): void => {
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const url = `${API_URL}/api/export/podcast/${podcastId}/audio`;
    const a = document.createElement('a');
    a.href = url;
    a.download = '';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  },

  /**
   * Download podcast cover image as PNG.
   */
  downloadCover: (podcastId: string): void => {
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const url = `${API_URL}/api/export/podcast/${podcastId}/cover`;
    const a = document.createElement('a');
    a.href = url;
    a.download = '';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  },

  /**
   * Download full ZIP archive (audio + cover + RSS + metadata).
   */
  downloadZip: (podcastId: string): void => {
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const url = `${API_URL}/api/export/podcast/${podcastId}/zip`;
    const a = document.createElement('a');
    a.href = url;
    a.download = '';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  },

  /**
   * Get RSS feed URL for a podcast.
   */
  getRssFeedUrl: (podcastId: string): string => {
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    return `${API_URL}/api/rss/podcast/${podcastId}.xml`;
  },
};
