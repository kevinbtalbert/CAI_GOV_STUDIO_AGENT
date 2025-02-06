import React from 'react';
import { Handle, Position, NodeProps, Node } from '@xyflow/react';
import { Avatar, Layout, Typography } from 'antd';
import { FileDoneOutlined, UserOutlined } from '@ant-design/icons';
import { BaseNode } from '@/components/base-node';
import { AgentMetadata } from '@/studio/proto/agent_studio';

const { Text, Paragraph } = Typography;

type TaskNode = Node<
  {
    name: string;
    active: boolean;
  },
  'task'
>;

export default function TaskNode({ data }: NodeProps<TaskNode>) {
  return (
    <div
      style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px',
        background: '#f3f3f3',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
        border: data.active ? '5px solid #007bff' : 'none',
        animation: data.active ? 'pulse 1.5s infinite' : 'none',
        maxWidth: 150,
        backgroundColor: 'lightgreen',
      }}
    >
      {/* Ant Design Avatar */}
      <Avatar
        style={{
          position: 'absolute',
          top: -20,
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)', // Optional shadow for floating look,
          backgroundColor: '#26bd67',
        }}
        size={24}
        icon={<FileDoneOutlined />}
      />

      {/* Node Content */}
      <div
        style={{
          textAlign: 'center',
          fontWeight: 'regular',
        }}
      >
        <Paragraph
          ellipsis={{ rows: 2 }}
          style={{ padding: 0, margin: 0, fontSize: 8, fontWeight: 400 }}
        >
          {data.name}
        </Paragraph>
      </div>

      {/* Handles for React Flow */}
      <Handle type="source" position={Position.Bottom} style={{ background: '#555' }} />
    </div>
  );
}
