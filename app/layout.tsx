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
                  {children}
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
