import React from 'react';
import { Typography, Layout } from 'antd';
import { WarningOutlined } from '@ant-design/icons';
import { Model } from '@/studio/proto/agent_studio';
import Link from 'next/link';
import { useGetDefaultModelQuery } from '../models/modelsApi';

const { Text } = Typography;

const NoDefaultModelModal: React.FC = () => {
  const { data: defaultModel } = useGetDefaultModelQuery();

  if (defaultModel) {
    return null;
  }

  return (
    <Layout
      style={{
        background: '#fff2f0',
        border: '1px solid #ffccc7',
        borderRadius: '6px',
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexGrow: 0,
        padding: '10px 16px',
        marginBottom: '16px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', flex: 1 }}>
        <WarningOutlined
          style={{
            fontSize: '22px',
            color: '#ff4d4f',
          }}
        />
        <Text
          style={{
            marginLeft: '12px',
            color: '#434343',
          }}
        >
          The studio needs a default LLM model to work properly. Please{' '}
          <Link
            href="/models?promptNewModelRegistration=true"
            style={{ textDecoration: 'underline' }}
          >
            register a model
          </Link>{' '}
          to get started.
        </Text>
      </div>
    </Layout>
  );
};

export default NoDefaultModelModal;
