import apiClient from './api';

export interface TextExtractionResponse {
  text: string;
  source_type: string;
  error?: string;
}

export const textExtractionApi = {
  // Extract text from file
  extractFromFile: async (file: File): Promise<TextExtractionResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/text/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Extract text from URL
  extractFromUrl: async (url: string): Promise<TextExtractionResponse> => {
    const response = await apiClient.post('/text/url', { url });
    return response.data;
  },

  // Extract text from pasted text
  extractFromText: async (text: string): Promise<TextExtractionResponse> => {
    const response = await apiClient.post('/text/extract', { text });
    return response.data;
  },
};
