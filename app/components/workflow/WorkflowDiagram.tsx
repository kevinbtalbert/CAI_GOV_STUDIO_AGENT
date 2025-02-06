import { Layout } from 'antd';
import {
  applyEdgeChanges,
  applyNodeChanges,
  Background,
  Controls,
  Node,
  Edge,
  ReactFlow,
  useReactFlow,
  type NodeTypes,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { createDiagramStateFromWorkflow, DiagramState } from '../../workflows/diagrams';
import { useCallback, useEffect, useState } from 'react';
import AgentNode from '../diagram/AgentNode';
import TaskNode from '../diagram/TaskNode';
import ToolNode from '../diagram/ToolNode';
import { AgentMetadata, CrewAITaskMetadata, ToolInstance } from '@/studio/proto/agent_studio';
import { processEvents } from '@/app/lib/workflow';
import { WorkflowState } from '@/app/workflows/editorSlice';

const nodeTypes: NodeTypes = {
  agent: AgentNode,
  task: TaskNode,
  tool: ToolNode,
};

export interface WorkflowDiagramProps {
  workflowState: WorkflowState;
  toolInstances?: ToolInstance[];
  agents?: AgentMetadata[];
  tasks?: CrewAITaskMetadata[];
  events?: any[];
}

const WorkflowDiagram: React.FC<WorkflowDiagramProps> = ({
  workflowState,
  toolInstances,
  agents,
  tasks,
  events,
}) => {
  // React flow
  const { fitView } = useReactFlow();

  // Nodes and edges
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const onNodesChange = useCallback(
    (changes: any) => setNodes((prevState) => applyNodeChanges(changes, prevState)),
    [setNodes],
  );
  const onEdgesChange = useCallback(
    (changes: any) => setEdges((prevState) => applyEdgeChanges(changes, prevState)),
    [setEdges],
  );

  useEffect(() => {
    const diagramState: DiagramState = createDiagramStateFromWorkflow({
      workflowState,
      toolInstances,
      agents,
      tasks,
    });
    setNodes((prevState) => diagramState.nodes);
    setEdges((prevState) => diagramState.edges);
  }, [workflowState, toolInstances, agents, tasks]);

  useEffect(() => {
    setTimeout(() => {
      fitView({ padding: 0.2 });
    }, 0); // Ensure it's called after the state update
  }, [nodes, edges]);

  useEffect(() => {
    // Process events into active nodes
    const { activeNodes } = events
      ? processEvents(
          events,
          agents || [],
          tasks || [],
          toolInstances || [],
          workflowState.workflowMetadata.managerAgentId,
          workflowState.workflowMetadata.process,
        )
      : { activeNodes: [] };

    // Update nodes with pulsating border for active nodes
    setNodes((prevNodes) => {
      return prevNodes.map((node) => {
        const activeNode = activeNodes.find((n) => n.id === node.id);
        if (activeNode) {
          return {
            ...node,
            data: {
              ...node.data,
              active: true,
              info: activeNode.info,
            },
          };
        } else {
          return {
            ...node,
            data: {
              ...node.data,
              active: false,
              info: undefined,
            },
          };
        }
      });
    });
  }, [events]);

  return (
    <>
      <Layout
        style={{
          flexShrink: 0,
          flexGrow: 1,
          height: '100%',
          flexDirection: 'column',
          padding: 0,
          background: 'transparent',
        }}
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
        >
          <Controls />
          <Background />
        </ReactFlow>
      </Layout>
    </>
  );
};

export default WorkflowDiagram;
