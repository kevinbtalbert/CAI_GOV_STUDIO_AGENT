import { AgentMetadata, CrewAIWorkflowMetadata, Workflow } from '@/studio/proto/agent_studio';
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../lib/store';
import { WorkflowParameters } from '../lib/localStorage';

// We store workflow information right in the editor. ts-proto compiles
// everything to be non-optional in protobuf messages, but we need
// all optional fields for proper component loading.
export interface WorkflowMetadataState {
  agentIds?: string[];
  taskIds?: string[];
  managerAgentId?: string;
  process?: string;
  // managerModelId?: string;
}

// We store workflow information right in the editor. ts-proto compiles
// everything to be non-optional in protobuf messages, but we need
// all optional fields for proper component loading.
export interface WorkflowState {
  workflowId?: string;
  name?: string;
  workflowMetadata: WorkflowMetadataState;
  isConversational?: boolean;
}

export interface CreateAgentState {
  name?: string;
  role?: string;
  backstory?: string;
  goal?: string;
  tools?: string[]; // For tool instances
  toolTemplateIds?: string[]; // New field for tool templates
  agentId?: string;
}

export interface AgentViewState {
  isOpen?: boolean;
  addAgentStep?: 'Select' | 'Details' | 'Create';
  agentId?: string;
  createAgent: CreateAgentState;
}

interface EditorState {
  currentStep?: 'Agents' | 'Tasks' | 'Configure' | 'Test' | 'Deploy';
  workflow: WorkflowState;
  agentView: AgentViewState;
  workflowParameters: WorkflowParameters;
}

const initialState: EditorState = {
  currentStep: 'Agents',
  workflow: {
    workflowMetadata: {
      agentIds: [],
      taskIds: [],
    },
  },
  agentView: {
    createAgent: {},
  },
  workflowParameters: {},
};

export interface UpdateWorkflowParameters {
  workflowId: string;
  toolInstanceId: string;
  parameterName: string;
  value: string;
}

export const editorSlice = createSlice({
  name: 'editor',
  initialState,
  reducers: {
    updatedEditorStep: (
      state,
      action: PayloadAction<'Agents' | 'Tasks' | 'Configure' | 'Test' | 'Deploy'>,
    ) => {
      state.currentStep = action.payload;
    },

    updatedEditorWorkflowFromExisting: (state, action: PayloadAction<Workflow>) => {
      const workflow: Workflow = action.payload;
      state.workflow = {
        workflowId: workflow.workflow_id,
        name: workflow.name,
        isConversational: workflow.is_conversational,
        workflowMetadata: {
          agentIds: workflow.crew_ai_workflow_metadata?.agent_id,
          taskIds: workflow.crew_ai_workflow_metadata?.task_id,
          managerAgentId: workflow.crew_ai_workflow_metadata?.manager_agent_id,
          process: workflow.crew_ai_workflow_metadata?.process,
          // managerModelId: workflow.crew_ai_workflow_metadata?.manager_llm_model_provider_id,
        },
      };
    },

    updatedEditorWorkflowProcess: (state, action: PayloadAction<string>) => {
      state.workflow.workflowMetadata.process = action.payload;
    },

    updatedEditorWorkflowId: (state, action: PayloadAction<string | undefined>) => {
      state.workflow.workflowId = action.payload;
    },

    updatedEditorWorkflowName: (state, action: PayloadAction<string | undefined>) => {
      state.workflow.name = action.payload;
    },

    updatedEditorWorkflowIsConversational: (state, action: PayloadAction<boolean | undefined>) => {
      state.workflow.isConversational = action.payload;
    },

    updatedEditorWorkflowManagerAgentId: (state, action: PayloadAction<string | undefined>) => {
      state.workflow.workflowMetadata.managerAgentId = action.payload;
      state.workflow.workflowMetadata.agentIds = state.workflow.workflowMetadata.agentIds?.filter(
        (agentId) => agentId !== action.payload,
      );
    },

    // updatedEditorWorkflowManagerModelId: (state, action: PayloadAction<string | undefined>) => {
    //   state.workflow.workflowMetadata.managerModelId = action.payload;
    // },

    updatedEditorWorkflowAgentIds: (state, action: PayloadAction<string[] | undefined>) => {
      state.workflow.workflowMetadata.agentIds = action.payload;
    },

    updatedEditorWorkflowTaskIds: (state, action: PayloadAction<string[] | undefined>) => {
      state.workflow.workflowMetadata.taskIds = action.payload;
    },

    updatedEditorAgentViewStep: (state, action: PayloadAction<'Select' | 'Details' | 'Create'>) => {
      state.agentView.addAgentStep = action.payload;
    },

    updatedEditorAgentViewAgentId: (state, action: PayloadAction<string | undefined>) => {
      state.agentView.agentId = action.payload;
    },

    updatedEditorAgentViewOpen: (state, action: PayloadAction<boolean | undefined>) => {
      state.agentView.isOpen = action.payload;
    },

    updatedEditorAgentViewCreateAgentName: (state, action: PayloadAction<string | undefined>) => {
      state.agentView.createAgent.name = action.payload;
    },

    updatedEditorAgentViewCreateAgentRole: (state, action: PayloadAction<string | undefined>) => {
      state.agentView.createAgent.role = action.payload;
    },

    updatedEditorAgentViewCreateAgentBackstory: (
      state,
      action: PayloadAction<string | undefined>,
    ) => {
      state.agentView.createAgent.backstory = action.payload;
    },

    updatedEditorAgentViewCreateAgentGoal: (state, action: PayloadAction<string | undefined>) => {
      state.agentView.createAgent.goal = action.payload;
    },

    updatedEditorAgentViewCreateAgentState: (state, action: PayloadAction<CreateAgentState>) => {
      state.agentView.createAgent = action.payload;
    },

    addedEditorWorkflowAgent: (state, action: PayloadAction<string>) => {
      state.workflow.workflowMetadata.agentIds = [
        ...(state.workflow.workflowMetadata.agentIds ?? []),
        action.payload,
      ];
    },

    addedEditorWorkflowTask: (state, action: PayloadAction<string>) => {
      state.workflow.workflowMetadata.taskIds = [
        ...(state.workflow.workflowMetadata.taskIds ?? []),
        action.payload,
      ];
    },

    addedEditorToolInstanceToAgent: (state, action: PayloadAction<string>) => {
      state.agentView.createAgent.tools = [
        ...(state.agentView.createAgent.tools ?? []),
        action.payload,
      ];
    },

    updatedEditorAgentViewCreateAgentToolTemplates: (state, action: PayloadAction<string[]>) => {
      state.agentView.createAgent.toolTemplateIds = action.payload;
    },

    addedEditorToolTemplateToAgent: (state, action: PayloadAction<string>) => {
      state.agentView.createAgent.toolTemplateIds = [
        ...(state.agentView.createAgent.toolTemplateIds ?? []),
        action.payload,
      ];
    },

    removedEditorToolTemplateFromAgent: (state, action: PayloadAction<string>) => {
      state.agentView.createAgent.toolTemplateIds =
        state.agentView.createAgent.toolTemplateIds?.filter((id) => id !== action.payload);
    },

    removedEditorWorkflowTask: (state, action: PayloadAction<string>) => {
      state.workflow.workflowMetadata.taskIds = state.workflow.workflowMetadata.taskIds?.filter(
        (id) => id !== action.payload,
      );
    },

    updatedWorkflowParameter: (state, action: PayloadAction<UpdateWorkflowParameters>) => {
      const { workflowId, toolInstanceId, parameterName, value } = action.payload;

      state.workflowParameters[workflowId] ??= {};
      state.workflowParameters[workflowId][toolInstanceId] ??= { parameters: {} };

      state.workflowParameters[workflowId][toolInstanceId].parameters[parameterName] = value;
    },

    updatedWorkflowParameters: (state, action: PayloadAction<WorkflowParameters>) => {
      state.workflowParameters = action.payload;
    },

    resetEditor: (state) => {
      return initialState;
    },
  },
});

export const {
  updatedEditorStep,
  updatedEditorWorkflowFromExisting,
  updatedEditorWorkflowId,
  updatedEditorWorkflowName,
  updatedEditorWorkflowProcess,
  updatedEditorWorkflowIsConversational,
  updatedEditorWorkflowManagerAgentId,
  // updatedEditorWorkflowManagerModelId,
  updatedEditorWorkflowAgentIds,
  updatedEditorWorkflowTaskIds,
  updatedEditorAgentViewStep,
  updatedEditorAgentViewOpen,
  updatedEditorAgentViewAgentId,
  updatedEditorAgentViewCreateAgentName,
  updatedEditorAgentViewCreateAgentRole,
  updatedEditorAgentViewCreateAgentBackstory,
  updatedEditorAgentViewCreateAgentGoal,
  updatedEditorAgentViewCreateAgentState,
  addedEditorWorkflowAgent,
  addedEditorWorkflowTask,
  addedEditorToolInstanceToAgent,
  updatedEditorAgentViewCreateAgentToolTemplates,
  addedEditorToolTemplateToAgent,
  updatedWorkflowParameter,
  updatedWorkflowParameters,
  removedEditorToolTemplateFromAgent,
  removedEditorWorkflowTask,
  resetEditor,
} = editorSlice.actions;

export const selectEditor = (state: RootState) => state.editor;
export const selectEditorCurrentStep = (state: RootState) => state.editor.currentStep;
export const selectEditorWorkflow = (state: RootState) => state.editor.workflow;
export const selectEditorWorkflowId = (state: RootState) => state.editor.workflow.workflowId;
export const selectEditorWorkflowName = (state: RootState) => state.editor.workflow.name;
export const selectEditorWorkflowManagerAgentId = (state: RootState) =>
  state.editor.workflow.workflowMetadata.managerAgentId;
// export const selectEditorWorkflowManagerModelId = (state: RootState) =>
//   state.editor.workflow.workflowMetadata.managerModelId;
export const selectEditorWorkflowProcess = (state: RootState) =>
  state.editor.workflow.workflowMetadata.process;
export const selectEditorWorkflowIsConversational = (state: RootState) =>
  state.editor.workflow.isConversational;
export const selectEditorWorkflowAgentIds = (state: RootState) =>
  state.editor.workflow.workflowMetadata.agentIds;
export const selectEditorWorkflowTaskIds = (state: RootState) =>
  state.editor.workflow.workflowMetadata.taskIds;
export const selectEditorAgentViewStep = (state: RootState) => state.editor.agentView.addAgentStep;
export const selectEditorAgentViewAgentId = (state: RootState) => state.editor.agentView.agentId;
export const selectEditorAgentViewIsOpen = (state: RootState) => state.editor.agentView.isOpen;
export const selectEditorAgentViewCreateAgentName = (state: RootState) =>
  state.editor.agentView.createAgent.name;
export const selectEditorAgentViewCreateAgentRole = (state: RootState) =>
  state.editor.agentView.createAgent.role;
export const selectEditorAgentViewCreateAgentBackstory = (state: RootState) =>
  state.editor.agentView.createAgent.backstory;
export const selectEditorAgentViewCreateAgentGoal = (state: RootState) =>
  state.editor.agentView.createAgent.goal;
export const selectEditorAgentViewCreateAgentTools = (state: RootState) =>
  state.editor.agentView.createAgent.tools;
export const selectEditorAgentViewCreateAgentToolTemplates = (state: RootState) =>
  state.editor.agentView.createAgent.toolTemplateIds;
export const selectEditorAgentViewCreateAgentState = (state: RootState): CreateAgentState =>
  state.editor.agentView.createAgent;
export const selectWorkflowParameters = (state: RootState): WorkflowParameters =>
  state.editor.workflowParameters;

export default editorSlice.reducer;
