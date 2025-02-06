import {
  ListDeployedWorkflowsRequest,
  ListDeployedWorkflowsResponse,
  DeployedWorkflow,
  DeployWorkflowRequest,
  UndeployWorkflowRequest,
} from '@/studio/proto/agent_studio';

import { apiSlice } from '../api/apiSlice';

export const deployedWorkflowsApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    listDeployedWorkflows: builder.query<DeployedWorkflow[], ListDeployedWorkflowsRequest>({
      query: (request) => ({
        url: '/grpc/listDeployedWorkflows',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: ListDeployedWorkflowsResponse) => {
        return response.deployed_workflows;
      },
      providesTags: ['DeployedWorkflow'],
    }),
    undeployWorkflow: builder.mutation<void, UndeployWorkflowRequest>({
      query: (request) => ({
        url: '/grpc/undeployWorkflow',
        method: 'POST',
        body: request,
      }),
      invalidatesTags: ['DeployedWorkflow'],
    }),
  }),
});

export const { useListDeployedWorkflowsQuery, useUndeployWorkflowMutation } = deployedWorkflowsApi;
