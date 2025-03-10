'use client';

import React, { useEffect } from 'react';
import { AntdRegistry } from '@ant-design/nextjs-registry';
import 'antd/dist/reset.css';
import { Content } from 'antd/lib/layout/layout';
import Layout from 'antd/lib/layout/layout';
import './globals.css';
import StoreProvider from './components/StoreProvider';
import TopNav from './components/TopNav';
import { NotificationProvider } from './components/Notifications';
import { useHealthCheckQuery } from './lib/crossCuttingApi';
import { Spin, Typography } from 'antd';

const { Text } = Typography;

type ContentWithHealthCheckProps = {
  children: React.ReactNode;
};

const ContentWithHealthCheck: React.FC<ContentWithHealthCheckProps> = ({ children }) => {
  const { data: isHealthy, refetch: refetchHeathStatus } = useHealthCheckQuery();

  // Poll health check every second until backend is healthy
  useEffect(() => {
    if (!isHealthy) {
      const intervalId = setInterval(() => {
        refetchHeathStatus();
      }, 1000);

      // Clean up interval when component unmounts or when isHealthy becomes true
      return () => clearInterval(intervalId);
    }
  }, [isHealthy, refetchHeathStatus]);

  if (!isHealthy) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100%',
          flexDirection: 'column',
        }}
      >
        <Spin size="large" />
        <Text>Agent Studio is starting. Please wait...</Text>
      </div>
    );
  }

  return (
    <Content
      style={{
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        flex: 1,
        width: '100%',
      }}
    >
      {children}
    </Content>
  );
};

const RootLayout = ({ children }: React.PropsWithChildren) => {
  return (
    <>
      <html lang="en">
        <body>
          <AntdRegistry>
            <StoreProvider>
              <NotificationProvider>
                <Layout style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                  <TopNav />
                  <ContentWithHealthCheck>{children}</ContentWithHealthCheck>
                </Layout>
              </NotificationProvider>
            </StoreProvider>
          </AntdRegistry>
        </body>
      </html>
    </>
  );
};

export default RootLayout;
