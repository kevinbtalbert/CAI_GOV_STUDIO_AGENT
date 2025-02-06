import {
  Workflow,
  ListWorkflowsRequest,
  ListWorkflowsResponse,
  GetWorkflowRequest,
  GetWorkflowResponse,
  RemoveWorkflowRequest,
  TestWorkflowRequest,
  TestWorkflowResponse,
  UpdateWorkflowRequest,
  UpdateWorkflowResponse,
  AddWorkflowRequest,
  DeployWorkflowRequest,
  AddWorkflowResponse,
  WorkflowTemplateMetadata,
  ListWorkflowTemplatesRequest,
  ListWorkflowTemplatesResponse,
  GetWorkflowTemplateRequest,
  GetWorkflowTemplateResponse,
  AddWorkflowTemplateRequest,
  AddWorkflowTemplateResponse,
  RemoveWorkflowTemplateRequest,
} from '@/studio/proto/agent_studio';

import { apiSlice } from '../api/apiSlice';

export const workflowsApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    listWorkflows: builder.query<Workflow[], ListWorkflowsRequest>({
      query: (request) => ({
        url: '/grpc/listWorkflows',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: ListWorkflowsResponse) => {
        return response.workflows;
      },
      providesTags: ['Workflow'],
    }),
    getWorkflow: builder.mutation<Workflow, GetWorkflowRequest>({
      query: (request) => ({
        url: '/grpc/getWorkflow',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: GetWorkflowResponse) => {
        return response.workflow!;
      },
    }),
    getWorkflowById: builder.query<Workflow | undefined, string | undefined>({
      query: (request) => ({
        url: '/grpc/getWorkflow',
        method: 'POST',
        body: { workflow_id: request },
      }),
      transformResponse: (response: GetWorkflowResponse) => {
        return response.workflow;
      },
      providesTags: (result, error, workflow_id) =>
        result ? [{ type: 'Workflow', id: workflow_id }] : ['Workflow'],
    }),
    addWorkflow: builder.mutation<string, AddWorkflowRequest>({
      query: (request) => ({
        url: '/grpc/addWorkflow',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: AddWorkflowResponse) => {
        return response.workflow_id;
      },
      invalidatesTags: ['Workflow', 'Agent', 'ToolInstance', 'Task'],
    }),
    updateWorkflow: builder.mutation<void, UpdateWorkflowRequest>({
      query: (request) => ({
        url: '/grpc/updateWorkflow',
        method: 'POST',
        body: request,
      }),
      invalidatesTags: (result, error, request) =>
        request.workflow_id
          ? [{ type: 'Workflow', id: request.workflow_id }]
          : ['Workflow', 'Agent', 'ToolInstance', 'Task'],
    }),
    removeWorkflow: builder.mutation<void, RemoveWorkflowRequest>({
      query: (request) => ({
        url: '/grpc/removeWorkflow',
        method: 'POST',
        body: request,
      }),
      invalidatesTags: ['Workflow', 'Agent', 'ToolInstance', 'Task'],
    }),
    testWorkflow: builder.mutation<TestWorkflowResponse, TestWorkflowRequest>({
      query: (request) => ({
        url: '/grpc/testWorkflow',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: TestWorkflowResponse) => {
        return response;
      },
    }),
    deployWorkflow: builder.mutation<void, DeployWorkflowRequest>({
      query: (request) => ({
        url: '/grpc/deployWorkflow',
        method: 'POST',
        body: request,
      }),
      invalidatesTags: ['Workflow', 'DeployedWorkflow'],
    }),
    listWorkflowTemplates: builder.query<WorkflowTemplateMetadata[], ListWorkflowTemplatesRequest>({
      query: (request) => ({
        url: '/grpc/listWorkflowTemplates',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: ListWorkflowTemplatesResponse) => {
        return response.workflow_templates;
      },
      providesTags: ['WorkflowTemplate'],
    }),
    getWorkflowTemplate: builder.mutation<WorkflowTemplateMetadata, GetWorkflowTemplateRequest>({
      query: (request) => ({
        url: '/grpc/getWorkflowTemplate',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: GetWorkflowTemplateResponse) => {
        return response.workflow_template!;
      },
    }),
    getWorkflowTemplateById: builder.query<WorkflowTemplateMetadata, string>({
      query: (request) => ({
        url: '/grpc/getWorkflowTemplate',
        method: 'POST',
        body: { workflow_template_id: request },
      }),
      transformResponse: (response: GetWorkflowTemplateResponse) => {
        return response.workflow_template!;
      },
    }),
    addWorkflowTemplate: builder.mutation<string, AddWorkflowTemplateRequest>({
      query: (request) => ({
        url: '/grpc/addWorkflowTemplate',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: AddWorkflowTemplateResponse) => {
        return response.id;
      },
      invalidatesTags: ['WorkflowTemplate', 'AgentTemplate', 'ToolTemplate', 'TaskTemplate'],
    }),
    removeWorkflowTemplate: builder.mutation<void, RemoveWorkflowTemplateRequest>({
      query: (request) => ({
        url: '/grpc/removeWorkflowTemplate',
        method: 'POST',
        body: request,
      }),
      invalidatesTags: ['WorkflowTemplate', 'AgentTemplate', 'ToolTemplate', 'TaskTemplate'],
    }),
  }),
});

export const {
  useListWorkflowsQuery,
  useGetWorkflowMutation,
  useGetWorkflowByIdQuery,
  useRemoveWorkflowMutation,
  useTestWorkflowMutation,
  useUpdateWorkflowMutation,
  useDeployWorkflowMutation,
  useAddWorkflowMutation,
  useListWorkflowTemplatesQuery,
  useGetWorkflowTemplateMutation,
  useGetWorkflowTemplateByIdQuery,
  useAddWorkflowTemplateMutation,
  useRemoveWorkflowTemplateMutation,
} = workflowsApi;
