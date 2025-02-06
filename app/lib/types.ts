import {
  ToolInstance,
  DeployedWorkflow,
  ToolTemplate,
  Workflow,
  AgentMetadata,
  CrewAITaskMetadata,
} from '@/studio/proto/agent_studio';

export interface OpsData {
  ops_display_url: string;
}

export interface WorkflowData {
  renderMode: 'studio' | 'workflow';
  deployedWorkflowId: string;
  deployedWorkflow: DeployedWorkflow;
  workflowModelUrl: string;
  workflow: Workflow;
  agents: AgentMetadata[];
  tasks: CrewAITaskMetadata[];
  toolTemplates: ToolTemplate[];
  toolInstances: ToolInstance[];
}
