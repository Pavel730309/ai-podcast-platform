import { configureStore } from '@reduxjs/toolkit';
import podcastReducer from './podcastSlice';

export const store = configureStore({
  reducer: {
    podcast: podcastReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;