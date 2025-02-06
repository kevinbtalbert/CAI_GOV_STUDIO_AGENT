import React, { useState } from 'react';
import { Button, Layout, List, Typography, Popconfirm, Input, Divider, Space, Tooltip } from 'antd';
import { EditOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons';
import { useRouter } from 'next/navigation'; // Use Next.js router
import { ToolTemplate } from '@/studio/proto/agent_studio';
import { useImageAssetsData } from '@/app/lib/hooks/useAssetData';

const { Text } = Typography;
const { Search } = Input;

interface ToolsListProps {
  tools: ToolTemplate[];
  editExistingTemplate: (toolId: string) => void;
  deleteExistingTemplate: (templateId: string) => void;
}

const truncateText = (text: string, maxLength: number) => {
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text;
};

const ToolTemplateList: React.FC<ToolsListProps> = ({
  tools,
  editExistingTemplate,
  deleteExistingTemplate,
}) => {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const router = useRouter(); // Next.js router for navigation

  const { imageData } = useImageAssetsData(tools.map((tool) => tool.tool_image_uri));

  // Filter tools based on the search term
  const filteredTools = tools.filter((tool) =>
    tool.name.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <Layout
      style={{
        flex: 1,
        flexDirection: 'column',
        height: '100%',
        overflow: 'auto',
        width: '100%',
        background: 'transparent',
      }}
    >
      {/* Search Bar */}
      <Space direction="vertical" style={{ width: '100%', marginBottom: 16 }}>
        <Search
          placeholder="Search tools by name"
          allowClear
          enterButton={<SearchOutlined />}
          onSearch={(value) => setSearchTerm(value)}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </Space>

      {/* Tool List */}
      <List
        grid={{ gutter: 16 }}
        dataSource={filteredTools}
        renderItem={(item) => (
          <List.Item>
            <Layout
              style={{
                borderRadius: '4px',
                border: 'solid 1px #f0f0f0',
                backgroundColor: '#fff',
                width: '320px',
                height: '164px',
                margin: '0px 12px 16px 0px',
                padding: '0',
                display: 'flex',
                flexDirection: 'column',
                cursor: 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
              }}
              onClick={() => router.push(`/tools/view/${item.id}`)} // Navigate to tool details page
              onMouseEnter={(e: React.MouseEvent<HTMLElement>) => {
                e.currentTarget.style.transform = 'scale(1.03)';
                e.currentTarget.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
              }}
              onMouseLeave={(e: React.MouseEvent<HTMLElement>) => {
                e.currentTarget.style.transform = 'scale(1)';
                e.currentTarget.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
              }}
            >
              <Layout
                style={{
                  flex: 1,
                  background: 'transparent',
                  display: 'flex',
                  flexDirection: 'row',
                  alignItems: 'center',
                  paddingLeft: '24px',
                  paddingRight: '24px',
                }}
              >
                {/* Image */}
                {item.tool_image_uri && imageData[item.tool_image_uri] && (
                  <div
                    style={{
                      width: '24px',
                      height: '24px',
                      borderRadius: '50%',
                      background: '#f1f1f1', // Grey background
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      marginRight: '16px',
                    }}
                  >
                    {/* Icon - Only render if URI exists and image data is available */}
                    <img
                      src={imageData[item.tool_image_uri]}
                      alt={item.name}
                      style={{
                        width: '16px',
                        height: '16px',
                        objectFit: 'cover',
                        borderRadius: '2px', // Optional, based on design preference
                      }}
                    />
                  </div>
                )}
                {/* Text */}
                <div style={{ flex: 1, maxWidth: '220px' }}>
                  <Tooltip title={item.name}>
                    <Text
                      style={{
                        fontSize: '14px',
                        fontWeight: 400,
                        display: 'block',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}
                    >
                      {truncateText(item.name, 50)}
                    </Text>
                  </Tooltip>
                  <Tooltip title={item.tool_description || 'N/A'}>
                    <Text
                      style={{
                        paddingTop: '4px',
                        display: 'block',
                        fontSize: '11px',
                        opacity: 0.45,
                        fontWeight: 400,
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}
                    >
                      {truncateText(item.tool_description || 'N/A', 100)}
                    </Text>
                  </Tooltip>
                </div>
              </Layout>
              <Divider style={{ flexGrow: 0, margin: '0px' }} type="horizontal" />
              <Layout
                style={{
                  display: 'flex',
                  flexDirection: 'row',
                  flexGrow: 0,
                  background: 'transparent',
                  justifyContent: 'space-around',
                  alignItems: 'center',
                }}
              >
                {/* Edit Button */}
                <Tooltip
                  title={item.pre_built ? 'Prepackaged tools cannot be edited' : 'Edit Tool'}
                >
                  <Button
                    style={{ border: 'none' }}
                    icon={<EditOutlined style={{ opacity: 0.45 }} />}
                    disabled={item.pre_built}
                    onClick={(e) => {
                      e.stopPropagation(); // Prevent card click event
                      editExistingTemplate(item.id);
                    }}
                  />
                </Tooltip>
                <Divider style={{ flexGrow: 0, margin: '12px 0px' }} type="vertical" />
                {/* Delete Button */}
                <Tooltip
                  title={item.pre_built ? 'Prepackaged tools cannot be deleted' : 'Delete Tool'}
                >
                  <div>
                    {' '}
                    {/* Wrap in div so tooltip works when button disabled */}
                    <Popconfirm
                      title={`Delete ${item.name}?`}
                      description={`Are you sure you'd like to delete ${item.name}?`}
                      placement="topRight"
                      okText="Confirm"
                      cancelText="Cancel"
                      onConfirm={(e) => {
                        e?.stopPropagation(); // Prevent card click event
                        deleteExistingTemplate(item.id);
                      }}
                      onCancel={(e) => e?.stopPropagation()} // Prevent card click event
                    >
                      <Button
                        style={{ border: 'none' }}
                        icon={<DeleteOutlined style={{ opacity: 0.45 }} />}
                        disabled={item.pre_built}
                        onClick={(e) => e.stopPropagation()} // Prevent card click event
                      />
                    </Popconfirm>
                  </div>
                </Tooltip>
              </Layout>
            </Layout>
          </List.Item>
        )}
      />
    </Layout>
  );
};

export default ToolTemplateList;
