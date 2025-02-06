'use client';

import React from 'react';
import { Layout } from 'antd';
import { useGetWorkflowDataQuery } from '../workflows/workflowAppApi';
import StudioTopNav from './StudioTopNav';
import WorkflowTopNav from './WorkflowTopNav';

const { Header } = Layout;

const TopNav: React.FC = () => {
  const { data: workflowData, isLoading } = useGetWorkflowDataQuery();

  if (isLoading) {
    return <></>;
  }

  return workflowData?.renderMode === 'studio' ? <StudioTopNav /> : <></>;
};

export default TopNav;
