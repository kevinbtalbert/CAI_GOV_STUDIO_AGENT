'use client';

import React, { useState, useEffect } from 'react';
import {
  Button,
  Layout,
  List,
  Typography,
  Popconfirm,
  Input,
  Space,
  Divider,
  Tooltip,
  Image,
  Spin,
} from 'antd';
import {
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ExperimentOutlined,
} from '@ant-design/icons';
import { AgentTemplateMetadata } from '@/studio/proto/agent_studio';
import { useListGlobalToolTemplatesQuery } from '@/app/tools/toolTemplatesApi';
import { useRouter } from 'next/navigation';
import { useImageAssetsData } from '@/app/lib/hooks/useAssetData';

const { Text } = Typography;
const { Search } = Input;

interface AgentTemplateListProps {
  agentTemplates?: AgentTemplateMetadata[]; // Made optional for safety
  editExistingAgentTemplate: (templateId: string) => void;
  deleteExistingAgentTemplate: (templateId: string) => void;
  testAgentTemplate: (templateId: string) => void;
}

const truncateText = (text: string, maxWords: number) => {
  const words = text.split(' ');
  return words.length > maxWords ? `${words.slice(0, maxWords).join(' ')}...` : text;
};

const AgentList: React.FC<AgentTemplateListProps> = ({
  agentTemplates = [], // Default value to avoid undefined
  editExistingAgentTemplate,
  deleteExistingAgentTemplate,
  testAgentTemplate,
}) => {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [toolTemplateCache, setToolTemplateCache] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);
  const { data: toolTemplates = [] } = useListGlobalToolTemplatesQuery({});
  const router = useRouter();

  const { imageData: toolIconsData } = useImageAssetsData(
    toolTemplates.map((tool) => tool.tool_image_uri),
  );

  useEffect(() => {
    // Only proceed if toolTemplates has changed and is not empty
    if (!toolTemplates || toolTemplates.length === 0) return;

    // Move this outside of useEffect to avoid setting state during render
    const toolTemplateMap = toolTemplates.reduce((acc: Record<string, any>, template: any) => {
      acc[template.id] = {
        name: template.name,
        imageURI: template.tool_image_uri,
      };
      return acc;
    }, {});

    // Compare with current cache to avoid unnecessary updates
    if (JSON.stringify(toolTemplateMap) !== JSON.stringify(toolTemplateCache)) {
      setToolTemplateCache(toolTemplateMap);
    }
  }, [toolTemplates]); // Remove toolTemplateCache from dependencies

  const filteredAgentTemplates = agentTemplates.filter((template) =>
    template?.name?.toLowerCase().includes(searchTerm.toLowerCase()),
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
      <Space direction="vertical" style={{ width: '100%', marginBottom: 16 }}>
        <Search
          placeholder="Search agent templates by name"
          allowClear
          enterButton={<SearchOutlined />}
          onSearch={(value) => setSearchTerm(value)}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </Space>

      <List
        grid={{ gutter: 16 }}
        dataSource={filteredAgentTemplates}
        renderItem={(item) => (
          <List.Item>
            <Layout
              style={{
                borderRadius: '4px',
                border: 'solid 1px #f0f0f0',
                backgroundColor: '#fff',
                width: '400px',
                height: '190px',
                margin: '0px 12px 16px 0px',
                padding: '0',
                display: 'flex',
                flexDirection: 'column',
                cursor: 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
              }}
              onClick={() => router.push(`agents/edit/${item.id}`)}
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
                  flexDirection: 'column',
                  overflow: 'auto',
                }}
              >
                <Text
                  style={{
                    paddingTop: '24px',
                    paddingLeft: '24px',
                    paddingRight: '24px',
                    fontSize: '14px',
                    fontWeight: 400,
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}
                  title={item.name}
                >
                  {item.name}
                </Text>
                <Text
                  style={{
                    paddingTop: '4px',
                    paddingLeft: '24px',
                    paddingRight: '24px',
                    fontSize: '11px',
                    opacity: 0.45,
                    fontWeight: 400,
                  }}
                >
                  Goal:{' '}
                  <span
                    style={{
                      color: 'black', // Black for the agent goal
                      fontWeight: 400,
                    }}
                  >
                    {truncateText(item.goal || 'N/A', 5)}
                  </span>
                </Text>
                <Text
                  style={{
                    paddingTop: '4px',
                    paddingLeft: '24px',
                    paddingRight: '24px',
                    fontSize: '11px',
                    opacity: 0.45,
                    fontWeight: 400,
                  }}
                >
                  Backstory:{' '}
                  <span
                    style={{
                      color: 'black', // Black for the agent goal
                      fontWeight: 400,
                    }}
                  >
                    {truncateText(item.backstory || 'N/A', 5)}
                  </span>
                </Text>
                {item.tool_template_ids?.length > 0 && (
                  <Space
                    style={{
                      marginTop: '12px',
                      paddingLeft: '24px',
                      paddingRight: '24px',
                      display: 'flex',
                      flexWrap: 'wrap',
                      gap: '10px',
                    }}
                  >
                    {loading ? (
                      <Spin size="small" />
                    ) : (
                      item.tool_template_ids.map((toolTemplateId) => {
                        const toolTemplate = toolTemplateCache[toolTemplateId];
                        return toolTemplate ? (
                          <Tooltip title={toolTemplate.name} key={toolTemplateId} placement="top">
                            <div
                              style={{
                                width: '24px',
                                height: '24px',
                                borderRadius: '50%',
                                background: '#f1f1f1',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                              }}
                              onClick={(e) => e.stopPropagation()}
                            >
                              <Image
                                src={
                                  toolTemplate.imageURI && toolIconsData[toolTemplate.imageURI]
                                    ? toolIconsData[toolTemplate.imageURI]
                                    : '/fallback-image.png'
                                }
                                alt={toolTemplate.name}
                                width={16}
                                height={16}
                                preview={false}
                                style={{
                                  borderRadius: '2px',
                                  objectFit: 'cover',
                                }}
                              />
                            </div>
                          </Tooltip>
                        ) : null;
                      })
                    )}
                  </Space>
                )}
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
                <Button
                  style={{ border: 'none' }}
                  icon={<EditOutlined style={{ opacity: 0.45 }} />}
                  onClick={(e) => {
                    e.stopPropagation();
                    editExistingAgentTemplate(item.id);
                  }}
                />
                <Divider style={{ flexGrow: 0, margin: '12px 0px' }} type="vertical" />
                <Popconfirm
                  title={`Delete ${item.name}?`}
                  okText="Confirm"
                  cancelText="Cancel"
                  onConfirm={(e) => {
                    e?.stopPropagation();
                    deleteExistingAgentTemplate(item.id);
                  }}
                >
                  <Button
                    style={{ border: 'none' }}
                    icon={<DeleteOutlined style={{ opacity: 0.45 }} />}
                    onClick={(e) => e.stopPropagation()}
                  />
                </Popconfirm>
                <Divider style={{ flexGrow: 0, margin: '12px 0px' }} type="vertical" />
                <Button
                  style={{ border: 'none' }}
                  icon={<ExperimentOutlined style={{ opacity: 0.45 }} />}
                  onClick={(e) => {
                    e.stopPropagation();
                    testAgentTemplate(item.id);
                  }}
                  disabled
                />
              </Layout>
            </Layout>
          </List.Item>
        )}
      />
    </Layout>
  );
};

export default AgentList;
