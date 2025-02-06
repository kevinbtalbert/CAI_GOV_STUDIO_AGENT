import {
  ListTasksRequest,
  ListTasksResponse,
  GetTaskRequest,
  GetTaskResponse,
  AddTaskRequest,
  AddTaskResponse,
  CrewAITaskMetadata,
  RemoveTaskRequest,
  UpdateTaskRequest,
  ListTaskTemplatesRequest,
  ListTaskTemplatesResponse,
  GetTaskTemplateRequest,
  GetTaskTemplateResponse,
  TaskTemplateMetadata,
} from '@/studio/proto/agent_studio';

import { apiSlice } from '../api/apiSlice';

export const tasksApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    listTasks: builder.query<CrewAITaskMetadata[], ListTasksRequest>({
      query: (request) => ({
        url: '/grpc/listTasks',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: ListTasksResponse) => {
        return response.tasks;
      },
      providesTags: ['Task'],
    }),
    getTask: builder.mutation<CrewAITaskMetadata, GetTaskRequest>({
      query: (request) => ({
        url: '/grpc/getTask',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: GetTaskResponse) => {
        if (!response.task) {
          throw new Error('Task not found.'); // Throw an error if agent is undefined
        }
        return response.task;
      },
    }),
    addTask: builder.mutation<string, AddTaskRequest>({
      query: (request) => ({
        url: '/grpc/addTask',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: AddTaskResponse) => {
        return response.task_id;
      },
      invalidatesTags: ['Task'],
    }),
    updateTask: builder.mutation<void, UpdateTaskRequest>({
      query: (request) => ({
        url: '/grpc/updateTask',
        method: 'POST',
        body: request,
      }),
      transformResponse: () => {
        // No transformation needed as the API doesn't return a response body
        return;
      },
      invalidatesTags: ['Task'], // Ensure cache invalidation for agents
    }),
    removeTask: builder.mutation<void, RemoveTaskRequest>({
      query: (request) => ({
        url: '/grpc/removeTask',
        method: 'POST',
        body: request,
      }),
      invalidatesTags: ['Task'],
    }),
    listTaskTemplates: builder.query<TaskTemplateMetadata[], ListTaskTemplatesRequest>({
      query: (request) => ({
        url: '/grpc/listTaskTemplates',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: ListTaskTemplatesResponse) => {
        return response.task_templates;
      },
      providesTags: ['TaskTemplate'],
    }),
    getTaskTemplate: builder.query<TaskTemplateMetadata, GetTaskTemplateRequest>({
      query: (request) => ({
        url: '/grpc/getTaskTemplate',
        method: 'POST',
        body: request,
      }),
      transformResponse: (response: GetTaskTemplateResponse) => {
        if (!response.task_template) {
          throw new Error('Task template not found.');
        }
        return response.task_template;
      },
      providesTags: ['TaskTemplate'],
    }),
  }),
});

export const {
  useListTasksQuery,
  useGetTaskMutation,
  useAddTaskMutation,
  useUpdateTaskMutation,
  useRemoveTaskMutation,
  useListTaskTemplatesQuery,
  useGetTaskTemplateQuery,
} = tasksApi;
