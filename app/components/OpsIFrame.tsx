'use client';

import React, { useEffect, useRef, useState } from 'react';
import Content from 'antd/lib/layout';
import { Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import { useGetOpsDataQuery } from '../ops/opsApi';
import {
  selectCurrentEventIndex,
  selectCurrentEvents,
  selectCurrentPhoenixProjectId,
  selectWorkflowCurrentTraceId,
} from '../workflows/workflowAppSlice';
import { useAppSelector } from '../lib/hooks/hooks';

const OpsIFrame: React.FC = () => {
  const { data: opsData, isLoading } = useGetOpsDataQuery();
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [iframeUrl, setIFrameUrl] = useState(opsData?.ops_display_url);
  const [nodeUrl, setNodeUrl] = useState('/');
  const currentProjectId = useAppSelector(selectCurrentPhoenixProjectId);
  const currentTraceId = useAppSelector(selectWorkflowCurrentTraceId);

  useEffect(() => {
    if (opsData) {
      setIFrameUrl(opsData.ops_display_url);
    }
  }, [opsData]);

  useEffect(() => {
    console.log('effect');
    if (!currentProjectId || !currentTraceId || !opsData) {
      console.log('brutal');
      return;
    }

    setNodeUrl(`/projects/${currentProjectId}/traces/${currentTraceId}`);
  }, [currentProjectId, currentTraceId, opsData]);

  const loadingIndicator = <LoadingOutlined style={{ fontSize: 48 }} spin />;

  // This function will be called once the iframe has fully loaded
  const handleIFrameLoad = () => {
    if (!iframeRef.current) return;

    const iframeElement = iframeRef.current;
    // Both ways below can work, depending on the browser:
    const iframeDoc = iframeElement.contentDocument || iframeElement.contentWindow?.document;

    if (!iframeDoc) return;

    // Find all divs with both classes: 'ac-theme' and 'ac-theme--dark'
    const darkThemeDivs = iframeDoc.querySelectorAll('.ac-theme.ac-theme--dark');

    darkThemeDivs.forEach((div) => {
      div.classList.remove('ac-theme--dark');
      div.classList.add('ac-theme--light');
    });
  };

  return (
    <Content
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        overflow: 'hidden',
        flex: 1,
        width: '100%',
      }}
    >
      {!isLoading ? (
        <div style={{ flex: 1, overflow: 'hidden', width: '100%' }}>
          <iframe
            ref={iframeRef}
            src={`${iframeUrl}${nodeUrl}`}
            style={{ width: '100%', height: '100%', border: 'none' }}
            title="Embedded Content"
            onLoad={handleIFrameLoad}
          />
        </div>
      ) : (
        <Spin indicator={loadingIndicator} />
      )}
    </Content>
  );
};

export default OpsIFrame;
