import React from 'react';
import { Handle, Position, NodeProps, Node, NodeToolbar } from '@xyflow/react';
import { Avatar, Layout, Typography } from 'antd';
import { UsergroupAddOutlined, UserOutlined } from '@ant-design/icons';
import { BaseNode } from '@/components/base-node';
import { AgentMetadata } from '@/studio/proto/agent_studio';
import Markdown from 'react-markdown';

const { Text, Paragraph } = Typography;

export type InfoType = 'Completion' | 'TaskStart' | 'ToolInput' | 'ToolOutput';

type AgentNode = Node<
  {
    name: string;
    manager: boolean;
    active: boolean;
    info?: string;
    infoType?: InfoType;
  },
  'agent'
>;

export default function AgentNode({ data }: NodeProps<AgentNode>) {
  return (
    <div
      style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        padding: '16px',
        background: '#f3f3f3',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
        border: data.active ? '5px solid #007bff' : 'none',
        animation: data.active ? 'pulse 1.5s infinite' : 'none',
        maxWidth: 150,
        backgroundColor: data.manager ? 'white' : 'lightblue',
      }}
    >
      {data.info && (
        <>
          <NodeToolbar
            isVisible={true}
            className="rounded-sm bg-primary p-2 text-primary-foreground"
            position={Position.Top}
            tabIndex={1}
            style={{
              maxWidth: 500,
              opacity: 0.8,
              backgroundColor: '#1890ff',
            }}
          >
            <Paragraph
              ellipsis={{ rows: 8 }}
              style={{
                padding: 0,
                margin: 0,
                fontSize: 12,
                fontWeight: 300,
                color: 'white',
              }}
            >
              {data.info}
            </Paragraph>
          </NodeToolbar>
        </>
      )}

      <Avatar
        style={{
          position: 'absolute',
          left: -20, // Position avatar overlapping to the left
          top: -20,
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)', // Optional shadow for floating look
          backgroundColor: data.manager ? 'lightgrey' : '#4b85d1',
        }}
        size={36}
        icon={data.manager ? <UsergroupAddOutlined /> : <UserOutlined />}
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
      <Handle type="target" position={Position.Top} style={{ background: '#555' }} />
      <Handle type="source" position={Position.Bottom} style={{ background: '#555' }} />
    </div>
  );
}
