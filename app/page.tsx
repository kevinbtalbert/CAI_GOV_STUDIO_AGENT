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
        <Title level={1}>{wflowData.workflow.name}</Title>
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
