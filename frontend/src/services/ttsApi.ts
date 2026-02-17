import apiClient from './api';

export interface Voice {
  id: string;
  name: string;
  provider: string;
  gender: string;
  language: string;
  description?: string;
}

export const ttsApi = {
  // Get available voices
  getVoices: async (provider?: string, language?: string): Promise<Voice[]> => {
    const response = await apiClient.get('/tts/voices', {
      params: { provider, language },
    });
    return response.data;
  },

  // Generate preview for voice
  previewVoice: async (voiceId: string, text: string, provider = 'openai'): Promise<Blob> => {
    const response = await apiClient.post(
      '/tts/preview',
      { voice_id: voiceId, text, provider },
      { responseType: 'blob' }
    );
    return response.data;
  },

  // Synthesize text (for testing)
  synthesize: async (text: string, voiceId: string, provider = 'openai'): Promise<Blob> => {
    const response = await apiClient.post(
      '/tts/synthesize',
      { text, voice_id: voiceId, provider },
      { responseType: 'blob' }
    );
    return response.data;
  },
};
