import apiClient from './api';

export interface TextExtractionResponse {
  text: string;
  title?: string | null;
  author?: string | null;
  source_type: string;
  word_count: number;
  character_count: number;
  estimated_reading_time?: number;
  error?: string;
}

export const textExtractionApi = {
  /**
   * Upload a file (PDF/DOCX) and extract its text.
   * The backend has two separate endpoints:
   *   POST /text/upload  → returns { file_id, filename, ... }
   *   POST /text/extract/{file_id} → returns TextExtractionResponse
   */
  extractFromFile: async (file: File): Promise<TextExtractionResponse> => {
    // Step 1: upload the file
    const formData = new FormData();
    formData.append('file', file);

    const uploadResponse = await apiClient.post('/text/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    const { file_id } = uploadResponse.data as { file_id: string };

    // Step 2: extract text from the uploaded file
    const extractResponse = await apiClient.post(`/text/extract/${file_id}`);
    return extractResponse.data as TextExtractionResponse;
  },

  /**
   * Extract text from a URL.
   * Backend: POST /text/extract  { source_type: "url", url }
   */
  extractFromUrl: async (url: string): Promise<TextExtractionResponse> => {
    const response = await apiClient.post('/text/extract', {
      source_type: 'url',
      url,
    });
    return response.data as TextExtractionResponse;
  },

  /**
   * Process raw pasted text (clean + stats).
   * Backend: POST /text/extract  { source_type: "text", text }
   */
  extractFromText: async (text: string): Promise<TextExtractionResponse> => {
    const response = await apiClient.post('/text/extract', {
      source_type: 'text',
      text,
    });
    return response.data as TextExtractionResponse;
  },

  /**
   * Get list of supported file formats from the backend.
   */
  getSupportedFormats: async (): Promise<{ formats: string[]; max_file_size_mb: number }> => {
    const response = await apiClient.get('/text/supported-formats');
    return response.data;
  },
};
