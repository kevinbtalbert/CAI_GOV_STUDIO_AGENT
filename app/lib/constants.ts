import { WorkflowGenerationConfig, LocalStorageState } from './types';

/**
 * Default generation config parameters for our
 * workflows once they are first created. Currently, we only
 * support a shared generation config across all agents and
 * manager agents that make LLM calls.
 */
export const DEFAULT_GENERATION_CONFIG = {
  max_new_tokens: 4096,
  temperature: 0.7,
};

/**
 * Initial local storage state for a client browser. Note: we are not
 * setting any information about our workflow configuration yet, which is
 * done once a viewer enters the the workflows/create page for a
 * specific workflow.
 */
export const INITIAL_LOCAL_STORAGE_STAGE: LocalStorageState = {
  viewSettings: {
    displayIntroPage: true,
    showTour: true,
  },
};
