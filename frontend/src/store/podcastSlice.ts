import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface PodcastState {
  podcasts: any[];
  loading: boolean;
  error: string | null;
}

const initialState: PodcastState = {
  podcasts: [],
  loading: false,
  error: null,
};

export const podcastSlice = createSlice({
  name: 'podcast',
  initialState,
  reducers: {
    setPodcasts: (state, action: PayloadAction<any[]>) => {
      state.podcasts = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    addPodcast: (state, action: PayloadAction<any>) => {
      state.podcasts.unshift(action.payload);
    },
    updatePodcast: (state, action: PayloadAction<any>) => {
      const index = state.podcasts.findIndex(p => p.id === action.payload.id);
      if (index !== -1) {
        state.podcasts[index] = action.payload;
      }
    },
  },
});

export const { setPodcasts, setLoading, setError, addPodcast, updatePodcast } = podcastSlice.actions;

export default podcastSlice.reducer;