'use client';

import React, { useEffect, useState } from 'react';
import 'antd/dist/reset.css';
import WorkflowDataView from './components/WorkflowDataView';
import { Layout, Spin, Typography } from 'antd';
import { useGetWorkflowDataQuery } from './workflows/workflowAppApi';
import { initialState, LocalStorageState } from './lib/localStorage';
import HomeView from './components/HomeView';
import { useRouter } from 'next/navigation';
import { useAppDispatch } from './lib/hooks/hooks';
import { setRenderMode, setWorkflowModelUrl } from './lib/globalSettingsSlice';

const { Title, Text } = Typography;

const HomePage: React.FC = () => {
  const { data: wflowData, isLoading } = useGetWorkflowDataQuery();
  const [localStore, setLocalStore] = useState<LocalStorageState>();
  const router = useRouter();
  const dispatch = useAppDispatch();

  useEffect(() => {
    setLocalStore(
      window.localStorage.getItem('state')
        ? JSON.parse(window.localStorage.getItem('state')!)
        : initialState,
    );
  }, []);

  if (isLoading === true) {
    // Show a loading spinner while data is being fetched
    return (
      <div
        style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}
      >
        <Spin size="large" />
      </div>
    );
  }

  // Render workflow
  if (wflowData?.renderMode === 'workflow') {
    dispatch(setRenderMode('workflow'));
    dispatch(setWorkflowModelUrl(wflowData?.workflowModelUrl));
    return (
      <Layout
        style={{
          padding: 36,
          flexDirection: 'column',
        }}
      >
        <Layout style={{
          background: 'transparent',
          padding: 0,
          marginBottom: 12,
          flexDirection: 'row',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexGrow: 0,
          flexShrink: 0
        }}>
          <Title level={1} ellipsis style={{flexGrow: 1}}>{wflowData.workflow.name}</Title>
          <Layout style={{
            backgroundColor: '#132329',
            opacity: 0.7,
            borderRadius: 4,
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            flexGrow: 0,
            flexShrink: 0,
            padding: 12,
          }}>
            <Text className="font-sans" style={{fontSize: 12, fontWeight: 200, color: 'white'}}>built with</Text>
            <Text className="font-sans" style={{fontSize: 16, fontWeight: 200, color: 'white'}}>Cloudera <b>Agent Studio</b></Text>
          </Layout>
        </Layout>
        <WorkflowDataView workflowData={wflowData} />
      </Layout>
    );
  }

  if (!localStore) {
    // Show a loading spinner while local store data is being fetched
    return (
      <div
        style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}
      >
        <Spin size="large" />
      </div>
    );
  }

  if (localStore.viewSettings?.displayIntroPage === false) {
    // Show a loading spinner while we wait for workflows page.
    router.push('/workflows');
    return (
      <div
        style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}
      >
        <Spin size="large" />
      </div>
    );
  }

  dispatch(setRenderMode('studio'));
  dispatch(setWorkflowModelUrl(undefined));
  return <HomeView />;
};

export default HomePage;
