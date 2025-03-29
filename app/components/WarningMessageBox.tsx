import React from 'react';
import { Typography, Layout } from 'antd';
import { WarningOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface WarningMessageBoxProps {
  messageTrigger: boolean;
  message: React.ReactNode;
}

const WarningMessageBox: React.FC<WarningMessageBoxProps> = ({ messageTrigger, message }) => {
  if (!messageTrigger) {
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
          {message}
        </Text>
      </div>
    </Layout>
  );
};

export default WarningMessageBox;
