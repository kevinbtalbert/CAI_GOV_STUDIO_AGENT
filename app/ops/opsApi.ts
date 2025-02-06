import { apiSlice } from '../api/apiSlice';

import type { OpsData } from '@/app/lib/types';
export type { OpsData };

export interface KickoffCrewReponse {
  response: { trace_id: string };
}

export interface KickoffCrewRequest {
  workflowUrl: string;
  workflowInputs: Record<string, string>;
}

export const opsApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    getOpsData: builder.query<OpsData, void>({
      query: () => '/ops',
    }),
  }),
  overrideExisting: true,
});

export const { useGetOpsDataQuery } = opsApi;
