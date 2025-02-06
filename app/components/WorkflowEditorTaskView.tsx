import WorkflowEditorTaskInputs from './WorkflowEditorTaskInputs';
import { Divider, Layout } from 'antd';
import { useAppSelector } from '../lib/hooks/hooks';
import { selectEditorWorkflow } from '../workflows/editorSlice';
import { useListToolInstancesQuery } from '../tools/toolInstancesApi';
import { useListTasksQuery } from '../tasks/tasksApi';
import { useListAgentsQuery } from '../agents/agentApi';
import WorkflowDiagramView from './workflow/WorkflowDiagramView';

interface WorkflowEditorTaskViewProps {}

const WorkflowEditorTaskView: React.FC<WorkflowEditorTaskViewProps> = ({}) => {
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
        <WorkflowEditorTaskInputs></WorkflowEditorTaskInputs>
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

export default WorkflowEditorTaskView;
