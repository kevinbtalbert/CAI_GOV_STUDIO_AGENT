'use client';

import React from 'react';
import { AntdRegistry } from '@ant-design/nextjs-registry';
import 'antd/dist/reset.css';
import { Content } from 'antd/lib/layout/layout';
import Layout from 'antd/lib/layout/layout';
import './globals.css';
import StoreProvider from './components/StoreProvider';
import TopNav from './components/TopNav';
import { NotificationProvider } from './components/Notifications';

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
