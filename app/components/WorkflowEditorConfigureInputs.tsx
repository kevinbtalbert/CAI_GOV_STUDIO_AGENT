'use client';

import {
  Alert,
  Card,
  Input,
  Layout,
  Typography,
  Tag,
  Divider,
  Tooltip,
  Slider,
  InputNumber,
} from 'antd';
import { useListToolInstancesQuery } from '../tools/toolInstancesApi';
import { ToolInstance } from '@/studio/proto/agent_studio';
import { useListAgentsQuery } from '../agents/agentApi';
import { useAppDispatch, useAppSelector } from '../lib/hooks/hooks';
import {
  selectEditorWorkflowId,
  selectWorkflowConfiguration,
  selectWorkflowGenerationConfig,
  updatedWorkflowConfiguration,
  updatedWorkflowGenerationConfig,
  updatedWorkflowToolParameter,
} from '../workflows/editorSlice';
import {
  readWorkflowConfigurationFromLocalStorage,
  writeWorkflowConfigurationToLocalStorage,
} from '../lib/localStorage';
import { WorkflowGenerationConfig } from '../lib/types';
import { InfoCircleOutlined, QuestionCircleOutlined, UserOutlined } from '@ant-design/icons';
import { DEFAULT_GENERATION_CONFIG } from '../lib/constants';

const { Title, Text } = Typography;
const { Password } = Input;

export interface ToolConfigurationComponentProps {
  agentName: string;
  toolInstance: ToolInstance;
  workflowId: string;
}

export interface ToolInstanceMetadataProps {
  user_params?: string[];
}

/**
 * Set a workflow tool parameter value, of a specific parameter,
 * of a specific tool, of a specific workflow. Here, workflowConfiguration
 * will mutate.
 */
export const setWorkflowToolParameterInLocalStorage = (
  workflowId: string,
  toolId: string,
  parameterName: string,
  value: string,
): void => {
  try {
    const workflowConfiguration = readWorkflowConfigurationFromLocalStorage(workflowId);

    // Check to see if tool parameters are set
    if (!workflowConfiguration.toolConfigurations) {
      workflowConfiguration.toolConfigurations = {};
    }

    if (!workflowConfiguration.toolConfigurations[toolId]) {
      workflowConfiguration.toolConfigurations[toolId] = {
        parameters: {},
      };
    }

    workflowConfiguration.toolConfigurations[toolId].parameters[parameterName] = value;

    // Write updated state back to localStorage
    writeWorkflowConfigurationToLocalStorage(workflowId, workflowConfiguration);
  } catch (error) {
    console.error('Error setting configuration parameter:', error);
  }
};

/**
 * Set a generation config for this workflow.
 */
export const setGenerationConfig = (
  workflowId: string,
  generationConfig: WorkflowGenerationConfig,
) => {
  // Get local storage.
  const workflowConfiguration = readWorkflowConfigurationFromLocalStorage(workflowId);

  // Check to see if tool parameters are set
  if (!workflowConfiguration.generationConfig) {
    workflowConfiguration.generationConfig = {};
  }

  workflowConfiguration.generationConfig = {
    ...workflowConfiguration.generationConfig,
    ...generationConfig,
  };

  // Write updated state back to localStorage
  writeWorkflowConfigurationToLocalStorage(workflowId, workflowConfiguration);
};

const ToolConfigurationComponent: React.FC<ToolConfigurationComponentProps> = ({
  agentName,
  toolInstance,
  workflowId,
}) => {
  const instanceMetadata: ToolInstanceMetadataProps = JSON.parse(toolInstance.tool_metadata);
  const dispatch = useAppDispatch();

  // Grab the current tool configuration for this tool. NOTE: we do NOT
  // pull from local storage here. The only time we should be pulling workflow configuration from local
  // storage is when we first enter our workflow editor component for a given worklfow ID. Any time
  // other than this should only consiste of *write* operations to local storage.
  const workflowConfiguration = useAppSelector(selectWorkflowConfiguration);
  const toolConfiguration = workflowConfiguration.toolConfigurations[toolInstance.id] || {
    parameters: {},
  };

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
                  value={toolConfiguration.parameters[param]}
                  onChange={(e) => {
                    // We write both to redux (which encompasses the current editor state),
                    // as well as local storage.
                    dispatch(
                      updatedWorkflowToolParameter({
                        workflowId: workflowId,
                        toolInstanceId: toolInstance.id,
                        parameterName: param,
                        value: e.target.value,
                      }),
                    );
                    setWorkflowToolParameterInLocalStorage(
                      workflowId,
                      toolInstance.id,
                      param,
                      e.target.value,
                    );
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
  const workflowConfiguration = useAppSelector(selectWorkflowConfiguration);
  const workflowGenerationConfig = useAppSelector(selectWorkflowGenerationConfig);
  const dispatch = useAppDispatch();

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
      <Layout
        style={{
          background: 'transparent',
          width: '100%',
          flexGrow: 0,
        }}
      >
        <Title level={4}>Agents & Managers</Title>
        <Card title={<Text style={{ fontWeight: 500 }}>Generation</Text>}>
          <Layout
            style={{
              background: 'transparent',
              flexDirection: 'column',
              display: 'flex',
              flexGrow: 0,
              gap: 14,
            }}
          >
            <Layout
              style={{
                background: 'transparent',
                display: 'flex',
                flexDirection: 'row',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div
                style={{
                  justifyContent: 'flex-start',
                  alignItems: 'center',
                  display: 'flex',
                  flexGrow: 0,
                  gap: 4,
                }}
              >
                <Text style={{ fontSize: 14, fontWeight: 600 }}>Max New Tokens</Text>
                <Tooltip
                  title="Determines how many new tokens the agents and manager agent can generate while making LLM calls. There may be LLM endpoint restrictions on this value."
                  placement="right"
                >
                  <QuestionCircleOutlined />
                </Tooltip>
              </div>
              <InputNumber
                value={workflowGenerationConfig.max_new_tokens}
                onChange={(e) => {
                  dispatch(updatedWorkflowGenerationConfig({ max_new_tokens: e || undefined }));
                  writeWorkflowConfigurationToLocalStorage(workflowId!, {
                    ...workflowConfiguration,
                    generationConfig: {
                      ...workflowConfiguration.generationConfig,
                      max_new_tokens: e || undefined,
                    },
                  });
                }}
                style={{
                  width: 80,
                }}
              />
            </Layout>
            <Layout
              style={{
                background: 'transparent',
                display: 'flex',
                flexDirection: 'row',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div
                style={{
                  justifyContent: 'flex-start',
                  alignItems: 'center',
                  display: 'flex',
                  flexGrow: 0,
                  gap: 4,
                }}
              >
                <Text style={{ fontSize: 14, fontWeight: 600 }}>Temperature</Text>
                <Tooltip
                  title={
                    <>
                      Determines variation/creativity in agent LLM response. A higher temperature
                      value will lead to more varied and creative responses. A lower temperature
                      will lead to less varied and more deterministic responses.
                      <br />
                      <br />
                      NOTE: based on the LLM model used,{' '}
                      <b>exact determinism can not be guaranteed in between workflow runs.</b>
                    </>
                  }
                  placement="right"
                >
                  <QuestionCircleOutlined />
                </Tooltip>
              </div>
              <Slider
                min={0.0}
                max={1.0}
                step={0.01}
                defaultValue={DEFAULT_GENERATION_CONFIG.temperature}
                value={workflowGenerationConfig.temperature}
                onChange={(e) => {
                  dispatch(updatedWorkflowGenerationConfig({ temperature: e }));
                  writeWorkflowConfigurationToLocalStorage(workflowId!, {
                    ...workflowConfiguration,
                    generationConfig: {
                      ...workflowConfiguration.generationConfig,
                      temperature: e,
                    },
                  });
                }}
                style={{
                  flexGrow: 1,
                  marginLeft: 24,
                }}
              />
            </Layout>
          </Layout>
        </Card>
      </Layout>
      <Divider />
      <Layout
        style={{
          background: 'transparent',
          width: '100%',
          flexGrow: 0,
          gap: 12,
        }}
      >
        <Title level={4}>Tools</Title>
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
    </Layout>
  );
};

export default WorkflowEditorConfigureInputs;
