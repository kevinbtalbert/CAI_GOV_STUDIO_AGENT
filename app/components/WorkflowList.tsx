import React, { useState, useEffect } from 'react';
import { Layout, Typography, List, Alert, Tag } from 'antd';
import {
  Workflow,
  DeployedWorkflow,
  AgentMetadata,
  WorkflowTemplateMetadata,
  AgentTemplateMetadata,
} from '@/studio/proto/agent_studio';
import SearchBar from './WorkflowSearchBar';
import WorkflowListItem from './WorkflowListItem';
import { useListDeployedWorkflowsQuery } from '@/app/workflows/deployedWorkflowsApi';
import { useImageAssetsData } from '../lib/hooks/useAssetData';

const { Text } = Typography;

interface WorkflowListProps {
  workflows: Workflow[];
  deployedWorkflows: DeployedWorkflow[];
  agents: AgentMetadata[];
  workflowTemplates: WorkflowTemplateMetadata[];
  agentTemplates: AgentTemplateMetadata[];
  editWorkflow: (workflowId: string) => void;
  deleteWorkflow: (workflowId: string) => void;
  deleteWorkflowTemplate: (workflowTemplateId: string) => void;
  testWorkflow: (workflowId: string) => void;
  onDeploy: (workflow: Workflow) => void;
  onDeleteDeployedWorkflow: (deployedWorkflow: DeployedWorkflow) => void; // Added prop
}

const WorkflowList: React.FC<WorkflowListProps> = ({
  workflows,
  deployedWorkflows,
  agents,
  workflowTemplates,
  agentTemplates,
  editWorkflow,
  deleteWorkflow,
  deleteWorkflowTemplate,
  testWorkflow,
  onDeploy,
  onDeleteDeployedWorkflow,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const { imageData: agentIconsData } = useImageAssetsData(agents.map((_a) => _a.agent_image_uri));
  const { imageData: agentTemplateIconsData } = useImageAssetsData(
    agentTemplates.map((_a) => _a.agent_image_uri),
  );
  const combinedAgentIconsData = { ...agentIconsData, ...agentTemplateIconsData }; // two API calls to reduce load on backend?

  // Update the deployment status handling
  const { data: latestDeployments } = useListDeployedWorkflowsQuery(
    {},
    {
      pollingInterval: 10000,
    },
  );

  // Use latestDeployments if available, otherwise fall back to deployedWorkflows prop
  const currentDeployments = latestDeployments || deployedWorkflows;

  // Create the map from the current deployments
  const deployedWorkflowMap = currentDeployments.reduce<Record<string, DeployedWorkflow[]>>(
    (acc, dw) => {
      if (!acc[dw.workflow_id]) acc[dw.workflow_id] = [];
      acc[dw.workflow_id].push(dw);
      return acc;
    },
    {},
  );

  const filteredWorkflows = workflows.filter((workflow) =>
    workflow.name.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  // Modify to exclude workflows that are deployed from draft section
  const deployedWorkflowIds = new Set(Object.keys(deployedWorkflowMap));
  const draftWorkflows = filteredWorkflows.filter(
    (w) => w.is_draft && !deployedWorkflowIds.has(w.workflow_id),
  );

  return (
    <Layout
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        position: 'relative',
      }}
    >
      {/* Search Bar - Fixed at top */}
      <div
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 1,
          borderBottom: '1px solid #f0f0f0',
        }}
      >
        <SearchBar
          onSearch={(value) => setSearchTerm(value)}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Scrollable content area */}
      <div
        style={{
          overflowY: 'auto',
          height: 'calc(100% - 70px)',
        }}
      >
        {/* Deployed Workflows */}
        {Object.keys(deployedWorkflowMap).length > 0 && (
          <>
            <Text
              style={{
                fontSize: '18px',
                fontWeight: 600,
                marginTop: '5px',
                display: 'block',
                marginBottom: '10px',
              }}
            >
              Deployed Workflows
            </Text>
            <List
              grid={{
                gutter: 10,
                xs: 1,
                sm: 2,
                md: 3,
                lg: 4,
                xl: 5,
                xxl: 5,
              }}
              style={{ width: '100%', padding: 0 }}
              dataSource={Object.keys(deployedWorkflowMap).filter((workflowId) =>
                filteredWorkflows.some((w) => w.workflow_id === workflowId),
              )}
              renderItem={(workflowId) => {
                const workflow = workflows.find((w) => w.workflow_id === workflowId);
                const deployments = deployedWorkflowMap[workflowId] || [];

                return workflow ? (
                  <List.Item style={{ width: '100%' }}>
                    <WorkflowListItem
                      key={workflowId}
                      workflow={workflow}
                      deployments={deployments}
                      agents={agents}
                      agentIconsData={combinedAgentIconsData}
                      editWorkflow={editWorkflow}
                      deleteWorkflow={deleteWorkflow}
                      testWorkflow={testWorkflow}
                      onDeploy={onDeploy}
                      onDeleteDeployedWorkflow={onDeleteDeployedWorkflow}
                      sectionType="Deployed"
                    />
                  </List.Item>
                ) : null;
              }}
            />
          </>
        )}

        {/* Draft Workflows */}
        {draftWorkflows.length > 0 && (
          <>
            <Text
              style={{ fontSize: '18px', fontWeight: 600, marginTop: '25px', marginBottom: '10px' }}
            >
              Draft Workflows
            </Text>
            <List
              grid={{
                gutter: 10,
                xs: 1,
                sm: 2,
                md: 3,
                lg: 4,
                xl: 5,
                xxl: 5,
              }}
              style={{ width: '100%' }}
              dataSource={draftWorkflows}
              renderItem={(workflow) => (
                <List.Item style={{ width: '100%', marginTop: '10px' }}>
                  <WorkflowListItem
                    key={workflow.workflow_id}
                    workflow={workflow}
                    deployments={deployedWorkflowMap[workflow.workflow_id] || []}
                    agents={agents}
                    agentIconsData={combinedAgentIconsData}
                    editWorkflow={editWorkflow}
                    deleteWorkflow={deleteWorkflow}
                    testWorkflow={testWorkflow}
                    onDeploy={onDeploy}
                    onDeleteDeployedWorkflow={onDeleteDeployedWorkflow}
                    sectionType="Draft"
                  />
                </List.Item>
              )}
            />
          </>
        )}

        {/* Templates */}
        {workflowTemplates.length > 0 && (
          <>
            <Text
              style={{ fontSize: '18px', fontWeight: 600, marginTop: '25px', marginBottom: '10px' }}
            >
              Workflow Templates
            </Text>
            <List
              grid={{
                gutter: 10,
                xs: 1,
                sm: 2,
                md: 3,
                lg: 4,
                xl: 5,
                xxl: 5,
              }}
              style={{ width: '100%', marginTop: '10px' }}
              dataSource={workflowTemplates}
              renderItem={(workflowTemplate) => (
                <List.Item style={{ width: '100%', margin: 0 }}>
                  <WorkflowListItem
                    key={workflowTemplate.id}
                    workflowTemplate={workflowTemplate}
                    agentTemplates={agentTemplates}
                    agentIconsData={combinedAgentIconsData}
                    deleteWorkflowTemplate={deleteWorkflowTemplate}
                    sectionType="Template"
                  />
                </List.Item>
              )}
            />
          </>
        )}
      </div>
    </Layout>
  );
};

export default WorkflowList;
