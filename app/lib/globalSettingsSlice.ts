import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from './store';

interface GlobalSettingsState {
  renderMode: 'studio' | 'workflow';
  workflowModelUrl?: string;
}

const initialState: GlobalSettingsState = {
  renderMode: 'studio', // default value
  workflowModelUrl: undefined, // default value
};

const globalSettingsSlice = createSlice({
  name: 'globalSettings',
  initialState,
  reducers: {
    setRenderMode: (state, action: PayloadAction<'studio' | 'workflow'>) => {
      state.renderMode = action.payload;
    },
    setWorkflowModelUrl: (state, action: PayloadAction<string | undefined>) => {
      state.workflowModelUrl = action.payload;
    },
  },
});

export const { setRenderMode, setWorkflowModelUrl } = globalSettingsSlice.actions;

// Selectors
export const selectRenderMode = (state: RootState) => state.globalSettings.renderMode;
export const selectWorkflowModelUrl = (state: RootState) => state.globalSettings.workflowModelUrl;

export default globalSettingsSlice.reducer;
