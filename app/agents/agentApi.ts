import {
  ListAgentsRequest,
  ListAgentsResponse,
  GetAgentRequest,
  GetAgentResponse,
  AddAgentRequest,
  AddAgentResponse,
  AgentMetadata,
  RemoveAgentRequest,
  UpdateAgentRequest,
  TestAgentRequest,
  TestAgentResponse,
  GetAgentTemplateRequest,
  AddAgentTemplateRequest,
  ListAgentTemplatesResponse,
  AgentTemplateMetadata,
  GetAgentTemplateResponse,
  AddAgentTemplateResponse,
  RemoveAgentTemplateRequest,
  UpdateAgentTemplateRequest,
} from '@/studio/proto/agent_studio';

import { apiSlice } from '../api/apiSlice';

export const agentsApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    listAgents: builder.query<AgentMetadata[], ListAgentsRequest>({
      query: (request) => ({
        url: '/grpc/listAgents',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: ListAgentsResponse) => {
        return response.agents;
      },
      providesTags: ['Agent'],
    }),
    getAgent: builder.query<AgentMetadata, GetAgentRequest>({
      query: (request) => ({
        url: '/grpc/getAgent',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: GetAgentResponse) => {
        if (!response.agent) {
          throw new Error('Agent not found.'); // Throw an error if agent is undefined
        }
        return response.agent;
      },
      providesTags: (result, error, { agent_id }) =>
        result ? [{ type: 'Agent', id: agent_id }] : ['Agent'],
    }),
    addAgent: builder.mutation<string, AddAgentRequest>({
      query: (request) => ({
        url: '/grpc/addAgent',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: AddAgentResponse) => {
        return response.agent_id;
      },
      invalidatesTags: ['Agent', 'Workflow', 'ToolInstance'],
    }),
    updateAgent: builder.mutation<void, UpdateAgentRequest>({
      query: (request) => ({
        url: '/grpc/updateAgent',
        method: 'POST',
        body: request,
      }),
      transformResponse: () => {
        // No transformation needed as the API doesn't return a response body
        return;
      },
      invalidatesTags: ['Agent', 'Workflow', 'ToolInstance'], // Ensure cache invalidation for agents
    }),
    removeAgent: builder.mutation<void, RemoveAgentRequest>({
      query: (request) => ({
        url: '/grpc/removeAgent',
        method: 'POST',
        body: request,
      }),
      invalidatesTags: ['Agent', 'Workflow', 'ToolInstance'],
    }),
    testAgent: builder.mutation<TestAgentResponse, TestAgentRequest>({
      query: (request) => ({
        url: '/grpc/testAgent',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: TestAgentResponse) => {
        return response;
      },
    }),
    listGlobalAgentTemplates: builder.query<AgentTemplateMetadata[], void>({
      query: (request) => ({
        url: '/grpc/listAgentTemplates',
        method: 'POST',
        body: {},
      }),
      transformResponse: (response: ListAgentTemplatesResponse) => {
        return response.agent_templates.filter((template) => !template.workflow_template_id);
      },
      providesTags: ['AgentTemplate'],
    }),
    getAgentTemplate: builder.query<AgentTemplateMetadata, GetAgentTemplateRequest>({
      query: (request) => ({
        url: '/grpc/getAgentTemplate',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: GetAgentTemplateResponse) => {
        if (!response.agent_template) {
          throw new Error('Agent not found.'); // Throw an error if agent is undefined
        }
        return response.agent_template;
      },
      providesTags: ['AgentTemplate'],
    }),
    addAgentTemplate: builder.mutation<string, AddAgentTemplateRequest>({
      query: (request) => ({
        url: '/grpc/addAgentTemplate',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: AddAgentTemplateResponse) => {
        return response.id;
      },
      invalidatesTags: ['AgentTemplate'],
    }),
    removeAgentTemplate: builder.mutation<void, RemoveAgentTemplateRequest>({
      query: (request) => ({
        url: '/grpc/removeAgentTemplate',
        method: 'POST',
        body: request,
      }),
      invalidatesTags: ['AgentTemplate'],
    }),
    updateAgentTemplate: builder.mutation<void, UpdateAgentTemplateRequest>({
      query: (request) => ({
        url: '/grpc/updateAgentTemplate',
        method: 'POST',
        body: request,
      }),
      invalidatesTags: ['AgentTemplate'],
    }),
    listAllAgentTemplates: builder.query<AgentTemplateMetadata[], void>({
      query: () => ({
        url: '/grpc/listAgentTemplates',
        method: 'POST',
        body: {},
      }),
      transformResponse: (response: ListAgentTemplatesResponse) => {
        return response.agent_templates;
      },
      providesTags: ['AgentTemplate'],
    }),
  }),
});

export const {
  useListAgentsQuery,
  useGetAgentQuery, // Updated to use `useGetAgentQuery`
  useAddAgentMutation,
  useUpdateAgentMutation,
  useRemoveAgentMutation,
  useTestAgentMutation,
  useListGlobalAgentTemplatesQuery,
  useGetAgentTemplateQuery,
  useAddAgentTemplateMutation,
  useRemoveAgentTemplateMutation,
  useUpdateAgentTemplateMutation,
  useListAllAgentTemplatesQuery,
} = agentsApi;
