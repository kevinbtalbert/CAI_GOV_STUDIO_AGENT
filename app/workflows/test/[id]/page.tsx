'use client';

import React from 'react';
import { useParams } from 'next/navigation';
import CommonBreadCrumb from '@/app/components/CommonBreadCrumb';
import { Layout } from 'antd';
import { useGetWorkflowByIdQuery } from '../../workflowsApi';
import { useListToolInstancesQuery } from '@/app/tools/toolInstancesApi';
import { useListTasksQuery } from '@/app/tasks/tasksApi';
import { useListAgentsQuery } from '@/app/agents/agentApi';
import WorkflowApp from '@/app/components/workflow/WorkflowApp';

const TestWorkflowPage: React.FC = () => {
  const params = useParams();
  const workflowId = Array.isArray(params?.id) ? params.id[0] : params?.id;
  const { data: workflow, refetch: refetchWorkflow } = useGetWorkflowByIdQuery(workflowId);
  const { data: toolInstances } = useListToolInstancesQuery({});
  const { data: tasks } = useListTasksQuery({});
  const { data: agents } = useListAgentsQuery({});

  if (!workflowId) {
    return <div>Invalid workflow ID</div>;
  }

  return (
    <Layout style={{ padding: '16px 24px', flexDirection: 'column' }}>
      <CommonBreadCrumb
        items={[{ title: 'Agentic Workflows', href: '/workflows' }, { title: 'Test Workflow' }]}
      />
      <WorkflowApp
        workflow={workflow}
        refetchWorkflow={refetchWorkflow}
        toolInstances={toolInstances}
        agents={agents}
        tasks={tasks}
      />
    </Layout>
  );
};

export default TestWorkflowPage;
