'use client';

import { Alert, Card, Input, Layout, Typography, Tag } from 'antd';
import { useListToolInstancesQuery } from '../tools/toolInstancesApi';
import { ToolInstance } from '@/studio/proto/agent_studio';
import { useListAgentsQuery } from '../agents/agentApi';
import { useAppDispatch, useAppSelector } from '../lib/hooks/hooks';
import {
  selectEditorWorkflowId,
  selectWorkflowParameters,
  updatedWorkflowParameter,
  updatedWorkflowParameters,
} from '../workflows/editorSlice';
import { LocalStorageState } from '../lib/localStorage';
import { InfoCircleOutlined, UserOutlined } from '@ant-design/icons';
import { useEffect } from 'react';

const { Text } = Typography;
const { Password } = Input;

export interface ToolConfigurationComponentProps {
  agentName: string;
  toolInstance: ToolInstance;
  workflowId: string;
}

export interface ToolInstanceMetadataProps {
  user_params?: string[];
}

export const setConfigurationParameter = (
  workflowId: string,
  toolInstanceId: string,
  parameterName: string,
  value: string,
): void => {
  try {
    const rawState = localStorage.getItem('state');
    const storageState: LocalStorageState = rawState ? JSON.parse(rawState) : {};

    // Ensure all levels of the hierarchy exist
    if (!storageState.workflowParameters) {
      storageState.workflowParameters = {};
    }
    if (!storageState.workflowParameters[workflowId]) {
      storageState.workflowParameters[workflowId] = {};
    }
    if (!storageState.workflowParameters[workflowId][toolInstanceId]) {
      storageState.workflowParameters[workflowId][toolInstanceId] = { parameters: {} };
    }

    // Set the parameter value in the "parameters" field
    storageState.workflowParameters[workflowId][toolInstanceId].parameters[parameterName] = value;

    // Write updated state back to localStorage
    localStorage.setItem('state', JSON.stringify(storageState));
  } catch (error) {
    console.error('Error setting configuration parameter:', error);
  }
};

const ToolConfigurationComponent: React.FC<ToolConfigurationComponentProps> = ({
  agentName,
  toolInstance,
  workflowId,
}) => {
  const instanceMetadata: ToolInstanceMetadataProps = JSON.parse(toolInstance.tool_metadata);
  const workflowParameters = useAppSelector(selectWorkflowParameters);
  const dispatch = useAppDispatch();

  if (!instanceMetadata.user_params || instanceMetadata.user_params.length == 0) {
    return <></>;
  }

  return (
    <>
      <Card
        title={
          <Layout
            style={{
              background: 'transparent',
              flexGrow: 0,
              flexDirection: 'row',
              alignItems: 'center',
              gap: 12,
            }}
          >
            <Text style={{ fontWeight: 500 }}>{toolInstance.name}</Text>
            <Tag style={{ background: '#add8e6', margin: 0 }}>
              <Layout
                style={{
                  flexDirection: 'row',
                  alignItems: 'center',
                  gap: 4,
                  background: 'transparent',
                  padding: 4,
                }}
              >
                <UserOutlined />
                <Text style={{ fontSize: 11, fontWeight: 400 }}>Agent: {agentName}</Text>
              </Layout>
            </Tag>
          </Layout>
        }
        style={{
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
        }}
      >
        <Layout
          style={{
            background: 'transparent',
            flexGrow: 0,
            flexDirection: 'column',
            gap: 8,
          }}
        >
          {instanceMetadata.user_params?.map((param, index) => {
            return (
              <Layout
                key={index}
                style={{
                  flexDirection: 'column',
                  flexGrow: 0,
                  background: 'transparent',
                }}
              >
                <Text style={{ fontWeight: 300 }}>{param}</Text>
                <Password
                  placeholder={param}
                  value={workflowParameters[workflowId]?.[toolInstance.id]?.parameters?.[param]}
                  onChange={(e) => {
                    dispatch(
                      updatedWorkflowParameter({
                        workflowId: workflowId,
                        toolInstanceId: toolInstance.id,
                        parameterName: param,
                        value: e.target.value,
                      }),
                    );
                    setConfigurationParameter(workflowId, toolInstance.id, param, e.target.value);
                  }}
                />
              </Layout>
            );
          })}
        </Layout>
      </Card>
    </>
  );
};

const WorkflowEditorConfigureInputs: React.FC = () => {
  const { data: agents } = useListAgentsQuery({});
  const workflowId = useAppSelector(selectEditorWorkflowId);
  const { data: toolInstances } = useListToolInstancesQuery({});
  const dispatch = useAppDispatch();

  // On component mount, load data from local storage
  useEffect(() => {
    const rawState = localStorage.getItem('state');
    if (!rawState) {
      return;
    }
    const storageState: LocalStorageState = JSON.parse(rawState);
    if (storageState && storageState.workflowParameters) {
      dispatch(updatedWorkflowParameters(storageState.workflowParameters));
    }
  }, []);

  const hasConfigurableTools = agents
    ?.filter((agent) => agent.workflow_id === workflowId)
    .some((agent) => {
      const toolInstanceIds = agent.tools_id;
      const workflowTools = toolInstances?.filter((toolInstance) =>
        toolInstanceIds.includes(toolInstance.id),
      );
      return workflowTools?.some((tool) => JSON.parse(tool.tool_metadata)?.user_params?.length > 0);
    });

  return (
    <Layout
      style={{
        flexDirection: 'column',
        flexGrow: 0,
        flexShrink: 0,
        padding: '16px 24px',
        width: '40%',
        height: '100%',
        background: 'transparent',
        gap: '24px',
        overflow: 'auto',
      }}
    >
      {!hasConfigurableTools && (
        <Alert
          style={{ marginBottom: 16 }}
          message={
            <Layout
              style={{ flexDirection: 'column', gap: 4, padding: 0, background: 'transparent' }}
            >
              <Layout
                style={{
                  flexDirection: 'row',
                  alignItems: 'center',
                  gap: 8,
                  background: 'transparent',
                }}
              >
                <InfoCircleOutlined style={{ color: '#1890ff' }} />
                <Text style={{ fontSize: 13, fontWeight: 600, background: 'transparent' }}>
                  No Configuration Required
                </Text>
              </Layout>
              <Text style={{ fontSize: 13, fontWeight: 400, background: 'transparent' }}>
                This workflow has no tools that require configuration. You can proceed to test and
                deploy the workflow.
              </Text>
            </Layout>
          }
          type="info"
          showIcon={false}
          closable={false}
        />
      )}
      {agents
        ?.filter((agent) => agent.workflow_id === workflowId)
        .map((agent, index) => {
          const toolInstanceIds = agent.tools_id;
          const worklfowTools = toolInstances?.filter((toolInstance) =>
            toolInstanceIds.includes(toolInstance.id),
          );
          return (
            <>
              {worklfowTools?.map((toolInstance, index) => (
                <>
                  <ToolConfigurationComponent
                    agentName={agent.name}
                    toolInstance={toolInstance}
                    workflowId={workflowId!}
                  />
                </>
              ))}
            </>
          );
        })}
    </Layout>
  );
};

export default WorkflowEditorConfigureInputs;
