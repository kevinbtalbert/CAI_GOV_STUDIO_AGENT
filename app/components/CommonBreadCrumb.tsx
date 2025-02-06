import React from 'react';
import { Breadcrumb } from 'antd';
import { HomeOutlined } from '@ant-design/icons';
import Link from 'next/link';

interface BreadCrumbItem {
  title: string;
  href?: string;
  icon?: React.ReactNode;
}

interface CommonBreadcrumbProps {
  items: BreadCrumbItem[];
}

const CommonBreadCrumb: React.FC<CommonBreadcrumbProps> = ({ items }) => {
  const breadcrumbItems = [
    {
      title: (
        <Link href="/" style={{ display: 'inline-flex', alignItems: 'center' }}>
          <HomeOutlined />
          <span style={{ marginLeft: '8px' }}>Agent Studio</span>
        </Link>
      ),
    },
    ...items.map((item) => ({
      title: item.href ? (
        <Link href={item.href}>
          {item.icon && <span style={{ marginRight: '8px' }}>{item.icon}</span>}
          <span>{item.title}</span>
        </Link>
      ) : (
        <>
          {item.icon && <span style={{ marginRight: '8px' }}>{item.icon}</span>}
          <span>{item.title}</span>
        </>
      ),
    })),
  ];

  return <Breadcrumb style={{ marginBottom: '10px' }} items={breadcrumbItems} />;
};

export default CommonBreadCrumb;
