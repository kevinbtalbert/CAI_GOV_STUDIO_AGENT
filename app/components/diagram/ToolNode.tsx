import React from 'react';
import { Handle, Position, NodeProps, Node, NodeToolbar } from '@xyflow/react';
import { Avatar, Image, Typography } from 'antd';
import { ToolOutlined } from '@ant-design/icons';

const { Paragraph } = Typography;

type InfoType = 'Completion' | 'TaskStart' | 'ToolInput' | 'ToolOutput';

type ToolNode = Node<
  {
    name: string;
    iconData: string;
    active: boolean;
    info?: string;
    infoType?: InfoType;
  },
  'task'
>;

export default function ToolNode({ data }: NodeProps<ToolNode>) {
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
        backgroundColor: 'lightgray',
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

      {/* Ant Design Avatar */}
      <Avatar
        style={{
          position: 'absolute',
          bottom: -15,
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)', // Optional shadow for floating look,
          backgroundColor: 'white',
          padding: data.iconData ? 5 : 0,
        }}
        size={24}
        icon={
          data.iconData ? (
            <Image src={data.iconData} />
          ) : (
            <ToolOutlined style={{ opacity: 0.6, color: 'black' }} />
          )
        }
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
    </div>
  );
}
