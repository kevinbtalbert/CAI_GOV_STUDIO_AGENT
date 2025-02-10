import React, { useState } from 'react';
import { Handle, Position, NodeProps, Node, NodeToolbar } from '@xyflow/react';
import { Avatar, Image, Typography } from 'antd';
import { UsergroupAddOutlined, UserOutlined } from '@ant-design/icons';
import { useImageAssetsData } from '@/app/lib/hooks/useAssetData';
const { Paragraph } = Typography;

export type InfoType = 'Completion' | 'TaskStart' | 'ToolInput' | 'ToolOutput';

type AgentNode = Node<
  {
    name: string;
    iconData: string;
    manager: boolean;
    active: boolean;
    info?: string;
    infoType?: InfoType;
    isMostRecent?: boolean;
  },
  'agent'
>;

export default function AgentNode({ data }: NodeProps<AgentNode>) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        padding: '16px',
        background: '#f3f3f3',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
        border: isHovered ? '2px solid #007bff' : '2px solid rgba(0,0,0,0)',
        animation: data.active ? 'pulse-in-out 1.0s infinite ease-in-out' : 'none',
        maxWidth: 200,
        backgroundColor: data.manager ? 'white' : 'lightblue',
      }}
    >
      {data.info && (data.isMostRecent || isHovered) && (
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
              {isHovered ? data.info : 'Thinking...'}
            </Paragraph>
          </NodeToolbar>
        </>
      )}

      <Avatar
        style={{
          position: 'absolute',
          left: -30, // Position avatar overlapping to the left
          top: -30,
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)', // Optional shadow for floating look
          backgroundColor: data.manager ? 'lightgrey' : data.iconData ? '#b8d6ff' : '#78b2ff', // or lightblue
          padding: data.manager ? 0 : data.iconData ? 8 : 0,
        }}
        size={48}
        icon={
          data.manager ? (
            <UsergroupAddOutlined />
          ) : data.iconData ? (
            <Image src={data.iconData} alt={data.name} />
          ) : (
            <UserOutlined />
          )
        }
      />

      {/* Node Content */}
      <div
        style={{
          textAlign: 'center',
          fontWeight: 'regular',
          padding: 0,
        }}
      >
        <Paragraph
          ellipsis={{ rows: 2 }}
          style={{ padding: 0, margin: 0, fontSize: 14, fontWeight: 400 }}
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
