export interface TestWorkflowToolUserParameters {
  parameters: {
    [parameter: string]: string;
  };
}

export interface WorkflowToolParameters {
  // Key-value store where key is the
  // tool ID and the value is dict of
  // user parameters
  [parameter: string]: TestWorkflowToolUserParameters;
}

export interface WorkflowParameters {
  // Dictionary where key is the workflow ID
  // and the value is a new dictionary of
  // user parameters
  [tool: string]: WorkflowToolParameters;
}

export interface ViewSettings {
  displayIntroPage?: boolean;
  showTour?: boolean;
}

export interface LocalStorageState {
  workflowParameters?: WorkflowParameters;
  viewSettings?: ViewSettings;
}

export const initialState: LocalStorageState = {
  viewSettings: {
    displayIntroPage: true,
    showTour: true,
  },
};
