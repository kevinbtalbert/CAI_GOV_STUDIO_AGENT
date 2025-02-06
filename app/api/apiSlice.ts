import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const TagTypes = [
  'Model',
  'ToolTemplate',
  'ToolInstance',
  'Workflow',
  'WorkflowApp',
  'Ops',
  'Agent',
  'ExternalAgentFamily',
  'Task',
  'DeployedWorkflow',
  'AgentTemplate',
  'TaskTemplate',
  'WorkflowTemplate',
];

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  tagTypes: TagTypes.slice(),
  endpoints: () => ({}),
});
