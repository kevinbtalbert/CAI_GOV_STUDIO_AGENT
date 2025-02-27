'use client';

import React, { useState } from 'react';
import {
  readViewSettingsFromLocalStorage,
  writeViewSettingsToLocalStorage,
} from '../lib/localStorage';
import { Avatar, Button, Checkbox, Image, Input, Layout, Typography } from 'antd';
import '../globals.css';
import {
  CloudUploadOutlined,
  DeploymentUnitOutlined,
  FileDoneOutlined,
  SendOutlined,
  UsergroupAddOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { useRouter } from 'next/navigation';
import { ViewSettings } from '../lib/types';

const { Title, Text, Paragraph } = Typography;

export interface HomeViewBannerCardProps {
  title: string;
  icon: React.ReactNode;
  content: string;
}

const HomeViewBannerCard: React.FC<HomeViewBannerCardProps> = ({ title, icon, content }) => {
  return (
    <>
      <Layout
        style={{
          flexDirection: 'row',
          background: 'transparent',
          flexGrow: 0,
          flexShrink: 0,
          gap: 8,
          padding: 0,
        }}
      >
        <div style={{ flexShrink: 0 }}>{icon}</div>

        <Layout
          style={{
            flexDirection: 'column',
            background: 'tranparent',
            gap: 8,
          }}
        >
          <Text style={{ height: 24, fontSize: 16, fontWeight: 400 }}>{title}</Text>
          <Text style={{ height: 24, fontSize: 14, fontWeight: 400 }}>{content}</Text>
        </Layout>
      </Layout>
    </>
  );
};

const HomeViewBannerContent: React.FC = () => {
  const router = useRouter();

  const handleDontShowAgain = (dontShowAgain: boolean) => {
    const viewSettings: ViewSettings = readViewSettingsFromLocalStorage() || {};
    const updatedViewSettings: ViewSettings = {
      ...viewSettings,
      displayIntroPage: !dontShowAgain,
    };
    writeViewSettingsToLocalStorage(updatedViewSettings);
  };

  return (
    <Layout
      style={{
        background: 'transparent',
        flexDirection: 'column',
        justifyContent: 'center',
        paddingLeft: 64,
        paddingRight: 64,
        gap: 24,
        maxWidth: 800,
        flexGrow: 0,
      }}
    >
      <Title
        level={2}
        style={{
          color: '#120046',
          fontSize: 64,
          fontWeight: '600',
          paddingBottom: 8,
          margin: 0,
        }}
        className="font-sans"
      >
        Agent Studio
      </Title>
      <Paragraph style={{ fontSize: 14, fontWeight: '400', padding: 0, margin: 0 }}>
        A dedicated platform within the Cloudera AI ecosystem that empowers users to design, test,
        and deploy multi-agent workflows.
      </Paragraph>
      <HomeViewBannerCard
        title="Create Agent Workflows"
        icon={
          <Avatar
            icon={<DeploymentUnitOutlined />}
            style={{ backgroundColor: '#fff4cd', color: 'black' }}
          />
        }
        content="Start by creating a workflow assigning multiple agents, with configurations tailored to specific tasks and tools."
      />
      <HomeViewBannerCard
        title="Create Agents & Tools"
        icon={
          <Avatar
            icon={<UsergroupAddOutlined />}
            style={{ backgroundColor: '#edf7ff', color: 'black' }}
          />
        }
        content="Agents can be created as standalone entities, configured to work with tools, and reused across workflows."
      />
      <HomeViewBannerCard
        title="Assign Tasks"
        icon={
          <Avatar
            icon={<FileDoneOutlined />}
            style={{ backgroundColor: '#e5ffe5', color: 'black' }}
          />
        }
        content="Assign tasks to tell your agents what to do."
      />
      <HomeViewBannerCard
        title="Deploy Workflow"
        icon={
          <Avatar
            icon={<CloudUploadOutlined />}
            style={{ backgroundColor: '#f9eeff', color: 'black' }}
          />
        }
        content="Workflows can be deployed as standalone applications in Cloudera's AI Workbench, enabling other users to interact with and benefit from them for specific tasks."
      />
      <Layout
        style={{
          flexGrow: 0,
          flexDirection: 'row',
          alignItems: 'center',
          justifyContent: 'flex-start',
          paddingTop: 32,
          gap: 24,
        }}
      >
        <Button
          type="primary"
          style={{
            height: 40,
            borderRadius: 3,
            backgroundColor: '#0074d2',
          }}
          onClick={() => {
            router.push('/workflows');
          }}
        >
          Get Started
        </Button>
        <Checkbox onChange={(e) => handleDontShowAgain(e.target.checked)}>
          Don't show me this again
        </Checkbox>
      </Layout>
    </Layout>
  );
};

export interface HomeViewAgentToolTextCardProps {
  itemBackgroundColor: string;
  itemBorderColor: string;
  textColor: string;
  text: string;
  borderType: string;
}

const HomeViewAgentToolTextCard: React.FC<HomeViewAgentToolTextCardProps> = ({
  itemBackgroundColor,
  itemBorderColor,
  textColor,
  text,
  borderType,
}) => {
  return (
    <>
      <Text
        style={{
          height: 22,
          fontSize: 12,
          backgroundColor: `${itemBackgroundColor}`,
          color: `${textColor}`,
          padding: '1px 8px',
          flexShrink: 0,
          borderRadius: 4,
          border: `${borderType} 1px ${itemBorderColor}`,
        }}
      >
        {text}
      </Text>
    </>
  );
};

export interface HomeViewAgentToolCardProps {
  borderColor: string;
  itemBackgroundColor: string;
  itemBorderColor: string;
  textColor: string;
}

const HomeViewDiagramAgentToolCard: React.FC<HomeViewAgentToolCardProps> = ({
  borderColor,
  itemBackgroundColor,
  itemBorderColor,
  textColor,
}) => {
  return (
    <>
      <Layout
        style={{
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'flex-start',
          flexGrow: 0,
          flexShrink: 0,
          borderRadius: 10,
          padding: 8,
          gap: 8,
          border: `solid 1px ${borderColor}`,
        }}
      >
        <HomeViewAgentToolTextCard
          itemBorderColor={itemBorderColor}
          itemBackgroundColor={itemBackgroundColor}
          textColor={textColor}
          borderType="solid"
          text="Agent 1"
        />
        <Layout
          style={{
            background: 'transparent',
            flexDirection: 'row',
            gap: 8,
          }}
        >
          <HomeViewAgentToolTextCard
            itemBorderColor={itemBorderColor}
            itemBackgroundColor={itemBackgroundColor}
            textColor={textColor}
            borderType="dashed"
            text="Tool 1"
          />
          <HomeViewAgentToolTextCard
            itemBorderColor={itemBorderColor}
            itemBackgroundColor={itemBackgroundColor}
            textColor={textColor}
            borderType="dashed"
            text="Tool 2"
          />
        </Layout>
      </Layout>
    </>
  );
};

const HomeViewDiagramContent: React.FC = () => {
  return (
    <>
      <Layout
        style={{
          flexDirection: 'column',
          width: '50%',
          gap: 8,
          justifyContent: 'center',
          alignItems: 'center',
          flexGrow: 0,
        }}
      >
        <Image
          src="/ic-brand-developer-engineer.svg"
          style={{ width: 80, height: 80, color: '#5284ff', flexGrow: 0 }}
        />
        <Layout
          style={{
            flexDirection: 'row',
            justifyContent: 'center',
            alignItems: 'center',
            flexGrow: 0,
            flexShrink: 0,
            margin: 0,
            padding: 0,
            gap: 8,
          }}
        >
          <HomeViewDiagramAgentToolCard
            borderColor="#ff8400"
            itemBackgroundColor="#fff7e6"
            itemBorderColor="#ffd591"
            textColor="#fa8c16"
          />
          <HomeViewDiagramAgentToolCard
            borderColor="#4ccf4c"
            itemBackgroundColor="#f6ffed"
            itemBorderColor="#b7eb8f"
            textColor="#52c41a"
          />
          <HomeViewDiagramAgentToolCard
            borderColor="#c354ff"
            itemBackgroundColor="#f9f0ff"
            itemBorderColor="#d3adf7"
            textColor="#722ed1"
          />
        </Layout>
        <Layout
          style={{
            flexDirection: 'row',
            justifyContent: 'center',
            alignItems: 'center',
            flexGrow: 0,
            flexShrink: 0,
            margin: 0,
            padding: 0,
            gap: 72,
          }}
        >
          <Image src="vec1.svg" />
          <Image src="vec2.svg" />
          <Image src="vec3.svg" />
        </Layout>
        <Layout
          style={{
            flexDirection: 'row',
            gap: 28,
            justifyContent: 'center',
            alignItems: 'center',
            flexGrow: 0,
            margin: 0,
            padding: 0,
          }}
        >
          <HomeViewAgentToolTextCard
            itemBorderColor="#d9d9d9"
            itemBackgroundColor="rgba(0, 0, 0, 0.02)"
            textColor="rgba(0, 0, 0, 0.88)"
            borderType="solid"
            text="Task 1"
          />
          <HomeViewAgentToolTextCard
            itemBorderColor="#d9d9d9"
            itemBackgroundColor="rgba(0, 0, 0, 0.02)"
            textColor="rgba(0, 0, 0, 0.88)"
            borderType="solid"
            text="Task 2"
          />
          <HomeViewAgentToolTextCard
            itemBorderColor="#d9d9d9"
            itemBackgroundColor="rgba(0, 0, 0, 0.02)"
            textColor="rgba(0, 0, 0, 0.88)"
            borderType="solid"
            text="Task 3"
          />
        </Layout>
        <Layout
          style={{
            flexDirection: 'row',
            justifyContent: 'center',
            alignItems: 'center',
            flexGrow: 0,
            margin: 0,
            padding: 0,
          }}
        >
          <Image src="vec2.svg" />
        </Layout>
        <Button
          type="primary"
          style={{
            borderRadius: 2,
            backgroundColor: '#1890ff',
          }}
        >
          Test
        </Button>
        <Layout
          style={{
            flexDirection: 'row',
            justifyContent: 'center',
            alignItems: 'center',
            flexGrow: 0,
          }}
        >
          <Image src="vec2.svg" />
        </Layout>
        <Layout
          style={{
            backgroundColor: 'white',
            borderRadius: 12,
            boxShadow: '0 1px 4px 0 rgba(0, 0, 0, 0.2)',
            width: 317.8,
            height: 160.5,
            flexGrow: 0,
            padding: 12,
          }}
        >
          {/* Cloudera agent studio header */}
          <Layout
            style={{
              alignItems: 'center',
              justifyContent: 'flex-start',
              display: 'flex',
              flexDirection: 'row',
              backgroundColor: 'transparent',
              gap: '4px',
              flexGrow: 0,
            }}
          >
            <Image
              src="/cloudera-logo.svg"
              preview={false}
              color="gray"
              style={{
                width: 18.6,
              }}
            />
            <Image
              src="/cloudera-agent-studio-text.svg"
              preview={false}
              color="gray"
              style={{
                width: 47.4,
              }}
            />
          </Layout>
          <Layout
            style={{
              background: 'transparent',
              justifyContent: 'flex-end',
              flexGrow: 0,
              flexShrink: 0,
              flexDirection: 'row',
              paddingTop: 24,
              gap: 8,
            }}
          >
            <Text style={{ fontSize: 8, fontWeight: 300 }}>
              What are the most customer service complaints?
            </Text>
            <Avatar
              icon={<UserOutlined />}
              size={14}
              style={{ backgroundColor: '#f7c200', flexShrink: 0 }}
            />
          </Layout>
          <Layout
            style={{
              background: 'transparent',
              justifyContent: 'flex-start',
              alignItems: 'start',
              flexGrow: 0,
              flexShrink: 0,
              flexDirection: 'row',
              paddingTop: 24,
              gap: 8,
            }}
          >
            <Avatar
              icon={<UserOutlined />}
              size={14}
              style={{ backgroundColor: '#008cff', flexShrink: 0 }}
            />
            <Paragraph
              style={{
                fontSize: 8,
                fontWeight: 300,
                backgroundColor: '#f4f5f6',
                borderRadius: 3,
                padding: 4,
              }}
            >
              Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
              incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
              exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
            </Paragraph>
          </Layout>
        </Layout>

        <Layout
          style={{
            backgroundColor: 'white',
            borderRadius: 12,
            boxShadow: '0 1px 4px 0 rgba(0, 0, 0, 0.2)',
            width: 317.8,
            height: 40.1,
            flexGrow: 0,
            marginTop: 12,
            flexDirection: 'row',
            gap: 4.5,
            padding: 10,
            alignItems: 'center',
          }}
        >
          <Input
            style={{
              backgroundColor: '#f4f5f6',
              height: 22.3,
              fontSize: 10,
              border: 'none',
              borderRadius: 3,
            }}
            placeholder="Ask your question here"
          />
          <Button
            style={{
              backgroundColor: '#f4f5f6',
              border: 'none',
              height: 22.3,
              borderRadius: 3,
              width: 22.3,
              flexShrink: 0,
            }}
            icon={<SendOutlined style={{}} />}
          />
        </Layout>
      </Layout>
    </>
  );
};

const HomeView: React.FC = () => {
  return (
    <>
      <Layout
        style={{
          flex: 1,
          flexDirection: 'row',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <HomeViewBannerContent />
        <HomeViewDiagramContent />
      </Layout>
    </>
  );
};

export default HomeView;
