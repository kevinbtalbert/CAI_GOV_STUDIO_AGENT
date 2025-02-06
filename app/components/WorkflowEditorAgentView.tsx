import { useListAgentsQuery } from '../agents/agentApi';
import { useAppSelector } from '../lib/hooks/hooks';
import { useListTasksQuery } from '../tasks/tasksApi';
import { useListToolInstancesQuery } from '../tools/toolInstancesApi';
import { selectEditorWorkflow } from '../workflows/editorSlice';
import WorkflowEditorAgentInputs from './WorkflowEditorAgentInputs';
import { Divider, Layout } from 'antd';
import WorkflowDiagramView from './workflow/WorkflowDiagramView';

interface WorkflowEditorAgentViewProps {}

const WorkflowEditorAgentView: React.FC<WorkflowEditorAgentViewProps> = ({}) => {
  const workflowState = useAppSelector(selectEditorWorkflow);
  const { data: toolInstances } = useListToolInstancesQuery({});
  const { data: tasks } = useListTasksQuery({});
  const { data: agents } = useListAgentsQuery({});

  return (
    <>
      <Layout
        style={{
          flex: 1,
          flexDirection: 'row',
          backgroundColor: 'white',
          borderRadius: 4,
        }}
      >
        <WorkflowEditorAgentInputs />
        <Divider type="vertical" style={{ height: '100%', flexGrow: 0, flexShrink: 0 }} />
        <WorkflowDiagramView
          workflowState={workflowState}
          toolInstances={toolInstances}
          tasks={tasks}
          agents={agents}
          displayDiagnostics={false}
        />
      </Layout>
    </>
  );
};

export default WorkflowEditorAgentView;
