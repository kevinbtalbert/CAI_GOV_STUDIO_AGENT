'use client';

import React from 'react';
import { useGetDefaultModelQuery } from '../models/modelsApi';
import {
  COMPATIBILITY_WARNING_2_0_47,
  ENTITLEMENT_WARNING_ML_ENABLE_COMPOSABLE_AMPS,
  NO_DEFAULT_LLM_NOTIFICATION,
} from '../lib/constants';
import { useWorkbenchDetailsQuery } from '../lib/crossCuttingApi';
import { compareWorkbenchVersions } from '../lib/workbench';
import WarningMessageBox from './WarningMessageBox';
import { Layout } from 'antd';

const MessageBoxes: React.FC = () => {
  const { data: defaultModel } = useGetDefaultModelQuery();
  const { data: workbench } = useWorkbenchDetailsQuery();

  const currentWarningMessages = [
    {
      messageTrigger: !defaultModel,
      message: NO_DEFAULT_LLM_NOTIFICATION,
    },
  ];
  workbench &&
    workbench.gitSha &&
    currentWarningMessages.push({
      messageTrigger: compareWorkbenchVersions(workbench.gitSha, '2.0.47') < 0,
      message: COMPATIBILITY_WARNING_2_0_47,
    });
  workbench &&
    currentWarningMessages.push({
      messageTrigger: !workbench.enable_ai_studios,
      message: ENTITLEMENT_WARNING_ML_ENABLE_COMPOSABLE_AMPS,
    });

  return (
    <>
      {currentWarningMessages.map((warningMessage) =>
        warningMessage.messageTrigger ? (
          <>
            <Layout
              style={{
                padding: 10,
                flexGrow: 0,
                flexShrink: 0,
                paddingBottom: 0,
              }}
            >
              <WarningMessageBox
                message={warningMessage.message}
                messageTrigger={warningMessage.messageTrigger}
              />
            </Layout>
          </>
        ) : (
          <></>
        ),
      )}
    </>
  );
};

export default MessageBoxes;
