'use client';

import React from 'react';
import { WorkflowData } from '../lib/types';
import { Typography } from 'antd/lib';
const { Text, Title } = Typography;
import WorkflowApp from './workflow/WorkflowApp';

interface WorkflowDataViewProps {
  workflowData: WorkflowData;
}

const WorkflowDataView: React.FC<WorkflowDataViewProps> = ({ workflowData }) => {
  return (
    <>
      <WorkflowApp
        workflow={workflowData.workflow}
        refetchWorkflow={() => {}}
        tasks={workflowData.tasks}
        toolInstances={workflowData.toolInstances}
        agents={workflowData.agents}
      />
    </>
  );
};

export default WorkflowDataView;
