'use client';

import React, { useState } from 'react';
import { Button, Typography, Layout, Alert, notification, Image } from 'antd';
import { UserOutlined, ArrowRightOutlined } from '@ant-design/icons';
import { useRouter } from 'next/navigation';
import AgentList from '../components/AgentList';
import { useListGlobalAgentTemplatesQuery, useRemoveAgentTemplateMutation } from './agentApi';
import CommonBreadCrumb from '../components/CommonBreadCrumb';
import { useGlobalNotification } from '../components/Notifications';

const { Content } = Layout;
const { Text } = Typography;

const AgentsPage: React.FC = () => {
  const { data: agentTemplates, refetch } = useListGlobalAgentTemplatesQuery();
  const [removeAgentTemplate] = useRemoveAgentTemplateMutation();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const notificationApi = useGlobalNotification();
  const router = useRouter();

  const handleGetStarted = () => {
    router.push('/agents/new');
  };

  const editExistingAgentTemplate = (templateId: string) => {
    router.push(`/agents/edit/${templateId}`);
  };

  const deleteExistingAgentTemplate = async (templateId: string) => {
    try {
      notificationApi.info({
        message: 'Deleting Agent Template',
        description: 'Deleting the agent template...',
        placement: 'topRight',
      });

      await removeAgentTemplate({ id: templateId }).unwrap();
      refetch();

      notificationApi.success({
        message: 'Agent Template Deleted',
        description: 'Agent template deleted successfully!',
        placement: 'topRight',
      });
    } catch (error: any) {
      const errorMessage = error?.data?.error || 'Failed to delete agent template.';
      setSubmitError(errorMessage);
      notificationApi.error({
        message: 'Error Deleting Agent Template',
        description: errorMessage,
        placement: 'topRight',
      });
    }
  };

  const testAgentTemplate = (templateId: string) => {
    router.push(`/agents/test/${templateId}`);
  };

  return (
    <Layout style={{ flex: 1, padding: '16px 24px 22px', flexDirection: 'column' }}>
      <CommonBreadCrumb items={[{ title: 'Agent Template Catalog' }]} />
      {submitError && (
        <Alert
          message="Error"
          description={submitError}
          type="error"
          showIcon
          closable
          onClose={() => setSubmitError(null)}
          style={{ marginBottom: '10px' }}
        />
      )}
      <Layout>
        <Layout
          style={{
            background: '#fff',
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexGrow: 0,
            padding: '16px',
          }}
        >
          {/* Icon */}
          <div
            style={{
              width: '66px',
              height: '66px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              overflow: 'hidden',
              backgroundColor: '#e5ffe5',
              margin: '0px',
            }}
          >
            <Image src="/ic-brand-developer-engineer.svg" alt="Workflow Catalog Icon" />
          </div>
          {/* Descriptive Text */}
          <Layout
            style={{
              background: '#fff',
              flex: 1,
              marginLeft: '12px',
              flexDirection: 'column',
              display: 'flex',
            }}
          >
            <Text style={{ fontWeight: 600, fontSize: '18px' }}>Create Agent</Text>
            <Text style={{ fontWeight: 350 }}>
              The Agent Template Catalog is your centralized hub for managing AI agent templates.
              Register new templates, edit existing ones, and organize them seamlessly. Build and
              optimize agent templates to enhance workflows with ease.
            </Text>
          </Layout>
          {/* Register New Model Button */}
          <Button
            style={{
              marginLeft: '20px',
              marginRight: '16px',
              marginTop: '20px',
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              flexDirection: 'row-reverse',
            }}
            icon={<ArrowRightOutlined />}
            onClick={handleGetStarted}
          >
            Get Started
          </Button>
        </Layout>
        &nbsp;
        <AgentList
          agentTemplates={agentTemplates || []} // Pass `agentTemplates` correctly
          editExistingAgentTemplate={editExistingAgentTemplate}
          deleteExistingAgentTemplate={(templateId: string) => {
            deleteExistingAgentTemplate(templateId);
          }}
          testAgentTemplate={testAgentTemplate}
        />
      </Layout>
    </Layout>
  );
};

export default AgentsPage;
