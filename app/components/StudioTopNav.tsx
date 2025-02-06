'use client';

import React from 'react';
import { Image, Layout, Menu, Typography } from 'antd';
import { useRouter, usePathname } from 'next/navigation';
import '../globals.css';

const { Text, Title } = Typography;
const { Header } = Layout;

const menuItems = [
  { key: '/workflows', label: 'Agentic Workflows' },
  { key: '/tools', label: 'Tools Catalog' },
  { key: '/models', label: 'LLMs' },
];

const StudioTopNav: React.FC = () => {
  const router = useRouter();
  const pathname = usePathname();

  const getSelectedKey = () => {
    // Sort by key length in descending order to prioritize longer matches
    const matchedItem = [...menuItems]
      .sort((a, b) => b.key.length - a.key.length)
      .find((item) => pathname.startsWith(item.key));

    return matchedItem ? matchedItem.key : '/';
  };

  return (
    <>
      {/* Header component with logo, text, and menu items */}
      <Header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          width: '100%',
          padding: '16px 24px',
          backgroundColor: '#132329',
        }}
      >
        {/* Flex layout of the image logo and the text logo */}
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
          <Title
            level={1}
            style={{ fontSize: 20, color: 'white', fontWeight: 400 }}
            className="font-sans"
          >
            Agent Studio
          </Title>
        </Layout>

        {/* Navigation bar menu items */}
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[getSelectedKey()]} // Highlight the current route
          items={menuItems}
          onClick={(e) => router.push(e.key)} // Navigate using Next.js router
          style={{
            flex: 1,
            fontWeight: 'normal',
            padding: 0,
            justifyContent: 'flex-end',
            backgroundColor: '#132329',
          }}
        />
      </Header>
    </>
  );
};

export default StudioTopNav;
