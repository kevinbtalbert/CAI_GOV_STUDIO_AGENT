import { apiSlice } from '../api/apiSlice';

import type { WorkflowData } from '@/app/lib/types';
export type { WorkflowData };

export const workflowAppApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    getWorkflowData: builder.query<WorkflowData, void>({
      query: () => '/wflow',
    }),
  }),
  overrideExisting: true,
});

export const { useGetWorkflowDataQuery } = workflowAppApi;
