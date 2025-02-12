import React from 'react';

import { List, Layout, Typography, Space, Avatar, Alert } from 'antd';

const { Text } = Typography;

const FeedbackContent: React.FC = () => {
  const githubBaseUrl = 'https://github.com/cloudera/CAI_STUDIO_AGENT';
  const feedbackItems = [
    {
      title: 'Email Feedback',
      description: (
        <Text style={{ fontSize: 13, fontWeight: 300, opacity: 0.6 }}>
          Reach out to us at ai_feedback@cloudera.com
        </Text>
      ),
      avatar: '/mail.png',
      link: 'mailto:ai_feedback@cloudera.com',
    },
    {
      title: 'GitHub Discussions',
      description: (
        <Text style={{ fontSize: 13, fontWeight: 350, opacity: 0.6 }}>
          Join the discussion on{' '}
          <a href={githubBaseUrl} target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
        </Text>
      ),
      avatar: 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png',
      link: `${githubBaseUrl}/discussions`,
    },
  ];

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="small">
      <Alert
        style={{
          alignItems: 'flex-start',
          justifyContent: 'flex-start',
          padding: 8,
          width: '100%',
        }}
        message={
          <Layout style={{ width: '100%', background: 'transparent' }}>
            <Text style={{ fontSize: 13, fontWeight: 400 }}>
              {'We value your feedback! Reach out to us via email or join the discussion on GitHub. ' +
                'Your thoughts help us improve and grow.'}
            </Text>
          </Layout>
        }
        type="info"
        showIcon={false}
        closable={false}
      />
      <List
        itemLayout="horizontal"
        dataSource={feedbackItems}
        style={{
          width: '100%',
          paddingLeft: '20px',
        }}
        renderItem={(item) => (
          <List.Item>
            <List.Item.Meta
              avatar={
                <a href={item.link} target="_blank" rel="noopener noreferrer">
                  <Avatar src={item.avatar} />
                </a>
              }
              title={
                <a href={item.link} target="_blank" rel="noopener noreferrer">
                  {item.title}
                </a>
              }
              description={item.description}
            />
          </List.Item>
        )}
      />
    </Space>
  );
};

export default FeedbackContent;
