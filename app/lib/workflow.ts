import {
  AddWorkflowRequest,
  AgentMetadata,
  CrewAITaskMetadata,
  CrewAIWorkflowMetadata,
  ToolInstance,
  UpdateWorkflowRequest,
} from '@/studio/proto/agent_studio';
import { WorkflowState } from '../workflows/editorSlice';
import { InfoType } from '../components/diagram/AgentNode';

export interface ActiveNodeState {
  id: string;
  info?: string;
  infoType?: InfoType;
  isMostRecent?: boolean;
}

type ProcessedState = {
  activeNodes: ActiveNodeState[]; // IDs of nodes currently "in work"
};

const extractThought = (completion: string) => {
  return completion;
};

// Add this interface near the top with other interfaces
export interface WorkflowEvent {
  id: string;
  name: string;
  attributes: any;
}

export const processEvents = (
  events: WorkflowEvent[],
  agents: AgentMetadata[],
  tasks: CrewAITaskMetadata[],
  toolInstances: ToolInstance[],
  manager_agent_id: string | undefined,
  process: string | undefined,
): ProcessedState => {
  let activeNodes: ActiveNodeState[] = [];

  events.forEach((event: WorkflowEvent) => {
    const { name, attributes } = event;

    switch (name) {
      case 'Agent._start_task': {
        const agentId = event.attributes.agent_studio_id;
        if (agentId) {
          if (manager_agent_id && manager_agent_id === agentId) {
            activeNodes.push({
              id: 'manager-agent',
              info: `I am starting a task: "${event.attributes.task.description}"`,
              infoType: 'TaskStart',
            });
          } else {
            activeNodes.push({
              id: agentId,
              info: `I am starting a task: "${event.attributes.task.description}"`,
              infoType: 'TaskStart',
            });
          }
        } else {
          if (process === 'hierarchical' && !manager_agent_id) {
            // NOTE: For default managers, it turns out that Agent._start_task is never triggered. That's because a default LLM
            // isn't technically registered as an Agent in crew - it's only completions without an agent. So technically
            // this line will never be hit.
            activeNodes.push({
              id: 'manager-agent',
              info: `I am starting a task: "${event.attributes.task.description}"`,
              infoType: 'TaskStart',
            });
          }
        }
        break;
      }

      case 'completion': {
        // If there are no active nodes, it's assumed that this completion
        // is a DEFAULT MANAGER, which does not trigger an Agent._start_task
        // command, but rather only triggers completion thoughts.
        if (activeNodes.length == 0) {
          activeNodes.push({
            id: 'manager-agent',
            info: `${event.attributes.output.value}`,
            infoType: 'Completion',
          });
        } else {
          // Let's assume for completions that the completion happens with
          // the currently most recently activated node, which should be an agent.
          activeNodes[activeNodes.length - 1] = {
            ...activeNodes[activeNodes.length - 1],
            info: event.attributes.output ? `${event.attributes.output.value}` : undefined,
            infoType: 'Completion',
          };
        }

        break;
      }

      case 'Agent._end_task': {
        const agentId = event.attributes.agent_studio_id;
        if (agentId) {
          activeNodes = activeNodes.filter((node) => node.id !== agentId);
        }
        break;
      }

      case 'ToolUsage._use': {
        const toolName = event.attributes.tool.name;
        const toolInstance = toolInstances.find((ti) => ti.name === toolName)!;
        if (toolName !== 'Delegate work to coworker' && toolName !== 'Ask question to coworker') {
          const inputValue = JSON.parse(event.attributes.input.value);
          toolInstance &&
            activeNodes.push({
              id: toolInstance.id,
              info: inputValue.calling,
              infoType: 'ToolInput',
            });
        }
        break;
      }

      case 'ToolUsage._end_use': {
        const toolName = event.attributes.tool.name;
        const toolInstance = toolInstances.find((ti) => ti.name === toolName)!;
        toolInstance && (activeNodes = activeNodes.filter((node) => node.id !== toolInstance.id));
        break;
      }

      case 'Crew.complete': {
        activeNodes = [];
        break;
      }
    }
  });

  if (activeNodes.length > 0) {
    activeNodes[activeNodes.length-1].isMostRecent = true;
  }

  return { activeNodes };
};

export const getWorkflowInputs = (
  workflowMetadata?: CrewAIWorkflowMetadata,
  tasks?: CrewAITaskMetadata[],
) => {
  const inputSet = new Set<string>();

  workflowMetadata?.task_id.forEach((task_id) => {
    const task = tasks?.find((task) => task.task_id === task_id);
    if (task) {
      task.inputs.forEach((input) => inputSet.add(input));
    }
  });

  return Array.from(inputSet);
};

export const createUpdateRequestFromEditor = (workflowState: WorkflowState) => {
  // There is a chance that the process is not yet defined. Let's fix that here.
  // In reality there should be validations further upstream.
  const managerAgentId = workflowState.workflowMetadata.managerAgentId;
  const process = workflowState.workflowMetadata.process || 'sequential';

  const updateRequest: UpdateWorkflowRequest = {
    workflow_id: workflowState.workflowId!,
    name: workflowState.name!,
    is_conversational: workflowState.isConversational!,
    crew_ai_workflow_metadata: {
      agent_id: workflowState.workflowMetadata.agentIds || [],
      task_id: workflowState.workflowMetadata.taskIds || [],
      manager_agent_id: managerAgentId || '',
      process: process,
    },
  };
  return updateRequest;
};

export const createAddRequestFromEditor = (workflowState: WorkflowState) => {
  // There is a chance that the process is not yet defined. Let's fix that here.
  // In reality there should be validations further upstream.
  const managerAgentId = workflowState.workflowMetadata.managerAgentId;
  const process = workflowState.workflowMetadata.process || 'sequential';

  console.log(workflowState);
  const addRequest: AddWorkflowRequest = {
    name: workflowState.name!,
    is_conversational: workflowState.isConversational!,
    crew_ai_workflow_metadata: {
      agent_id: workflowState.workflowMetadata.agentIds || [],
      task_id: workflowState.workflowMetadata.taskIds || [],
      manager_agent_id: managerAgentId || '',
      process: process,
    },
  };
  return addRequest;
};
