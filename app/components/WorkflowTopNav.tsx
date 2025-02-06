'use client';

import React from 'react';
import { Image, Layout, Menu, Typography } from 'antd';
import { useRouter, usePathname } from 'next/navigation';
import { WorkflowData } from '../lib/types';

const { Header } = Layout;

const menuItems = [];

interface WorkflowTopNavProps {
  workflowData?: WorkflowData;
}

const WorkflowTopNav: React.FC<WorkflowTopNavProps> = ({ workflowData }) => {
  const router = useRouter();
  const pathname = usePathname();

  return (
    <>
      {/* Header component with logo, text, and menu items */}
      <Header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          width: '100%',
          padding: '16px 24px',
          backgroundColor: '#132329',
        }}
      >
        {/* Flex layout of the image logo and the text logo */}
        <Layout
          style={{
            alignItems: 'center',
            justifyContent: 'flex-start',
            display: 'flex',
            flexDirection: 'row',
            backgroundColor: 'transparent',
            gap: '4px',
            flexGrow: 0,
          }}
        >
          <Image
            src="/cloudera-logo.svg"
            preview={false}
            style={{
              width: '40px',
            }}
          />
          <Image
            src="/cloudera-agent-studio-text.svg"
            preview={false}
            style={{
              width: '86px',
            }}
          />
        </Layout>

        {/* Navigation bar menu items */}
        <Layout
          style={{
            flex: 1,
            fontWeight: 'normal',
            padding: 0,
            flexGrow: 1,
            justifyContent: 'flex-end',
            alignItems: 'center',
            backgroundColor: 'transparent',
          }}
        >
          <Typography style={{ alignSelf: 'end', color: 'white' }}>
            Workflow: {workflowData?.deployedWorkflow.deployed_workflow_name}
          </Typography>
        </Layout>
      </Header>
    </>
  );
};

export default WorkflowTopNav;
