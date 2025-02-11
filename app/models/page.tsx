'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { Layout, Typography, Button, Form } from 'antd';
import { PlusCircleOutlined } from '@ant-design/icons';
import ModelList from '../components/ModelList';
import { AddModelRequest, Model } from '@/studio/proto/agent_studio';
import {
  useAddModelMutation,
  useGetModelMutation,
  useListModelsQuery,
  useRemoveModelMutation,
  useTestModelMutation,
  useUpdateModelMutation,
  useSetDefaultModelMutation,
} from './modelsApi';
import { useSearchParams } from 'next/navigation';
import NoDefaultModelModal from '../components/NoDefaultModelModal';
import CommonBreadCrumb from '../components/CommonBreadCrumb';
import ModelActionsDrawer from '../components/ModelActionsDrawer';

const { Title } = Typography;

// Main Component
const ModelsPage = () => {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ModelsPageContent />
    </Suspense>
  );
};

// Move all the existing component logic into ModelsPageContent
const ModelsPageContent = () => {
  const { data: models } = useListModelsQuery({});
  const [getModel] = useGetModelMutation();
  const [updateModel] = useUpdateModelMutation();
  const [addModel] = useAddModelMutation();
  const [testModel] = useTestModelMutation();
  const [removeModel] = useRemoveModelMutation();
  const [setDefaultModel] = useSetDefaultModelMutation();

  // const [models, setModels] = useState<Model[]>([]);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [drawerMode, setDrawerMode] = useState<'register' | 'edit' | 'test'>('register');
  const [selectedModel, setSelectedModel] = useState<Model | null>(null);
  const [changedModel, setChangedModel] = useState<AddModelRequest | null>(null);
  const [testMessage, setTestMessage] = useState<string>('');
  const [testResponse, setTestResponse] = useState<string | null>(null);
  const [modelTestStatus, setModelTestStatus] = useState<
    Record<string, 'success' | 'failure' | 'pending'>
  >({});
  const [form] = Form.useForm();
  const searchParams = useSearchParams();
  const [setModelAsDefault, setSetModelAsDefault] = useState(false);

  useEffect(() => {
    if (models) {
      models.forEach((model) => {
        if (!(model.model_id in modelTestStatus)) {
          aysncTestModelWithRetry(model.model_id);
        }
      });
    }
  }, [models]);

  const openCreateModelDrawer = () => {
    setSubmitError(null);
    setSubmitSuccess(null);
    form.resetFields();
    setSelectedModel(null);
    setDrawerMode('register');
    setIsDrawerOpen(true);
  };

  const openEditModelDrawer = async (modelId: string) => {
    try {
      const model = await getModel({ model_id: modelId }).unwrap();
      if (!model) throw new Error('Model not found.');
      setSelectedModel(model);
      form.setFieldsValue({
        modelAlias: model.model_name,
        modelProvider: model.model_type,
      });
      setSubmitError(null);
      setSubmitSuccess(null);
      setTestMessage('');
      setTestResponse(null);
      setDrawerMode('edit');
      setIsDrawerOpen(true);
    } catch (error: any) {
      setSubmitError(error.message || 'Failed to load model details.');
    }
  };

  const openTestModelDrawer = async (modelId: string) => {
    try {
      const model = await getModel({ model_id: modelId }).unwrap();
      if (!model) throw new Error('Model not found.');
      setSelectedModel(model);
      setSubmitError(null);
      setSubmitSuccess(null);
      setDrawerMode('test');
      setTestResponse(null);
      setIsDrawerOpen(true);
    } catch (error: any) {
      setSubmitError(error.message || 'Failed to load model details.');
    }
  };

  const aysncTestModelWithRetry = async (modelId: string) => {
    // Initially set the status to pending
    setModelTestStatus((prev) => ({ ...prev, [modelId]: 'pending' }));

    const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));
    const testMessage = 'Hello, this is a test message. Please respond.';
    // try for 15 seconds in total
    const attempts = 5;
    const delayBetweenAttempts = 3000; // 3 seconds

    let passed = false;
    for (let i = 0; i < attempts; i++) {
      try {
        const response = await testModel({
          model_id: modelId,
          completion_role: 'user',
          completion_content: testMessage,
          temperature: 0.1,
          max_tokens: 20,
          timeout: 2,
        }).unwrap();

        if (response.startsWith('Model Test Failed')) {
          console.warn(`Attempt ${i + 1}: Model test failed with response: ${response}`);
          await sleep(delayBetweenAttempts);
          continue;
        }

        // if we get here, the test passed
        passed = true;
        break;
      } catch (error) {
        console.error(`Attempt ${i + 1}: Error testing model -`, error);
        await sleep(delayBetweenAttempts);
      }
    }

    setModelTestStatus((prev) => ({ ...prev, [modelId]: passed ? 'success' : 'failure' }));
  };

  const handleFormSubmit = async (values: any) => {
    try {
      if (drawerMode === 'edit') {
        if (!selectedModel) throw new Error('Model not loaded for editing.');
        if (changedModel?.model_type !== selectedModel.model_type)
          throw new Error('Cannot change type when editing models.');
        await updateModel({
          model_id: selectedModel.model_id,
          model_name: changedModel?.model_name || '',
          provider_model: changedModel?.provider_model || '',
          api_base: changedModel?.api_base || '',
          api_key: changedModel?.api_key || '',
        });

        aysncTestModelWithRetry(selectedModel.model_id);
        setSubmitSuccess(`Model '${selectedModel.model_name}' updated successfully!`);
      } else {
        // register
        if (
          !changedModel?.model_name ||
          !changedModel?.api_key ||
          (['OPENAI_COMPATIBLE', 'AZURE_OPENAI'].includes(changedModel?.model_type) &&
            !changedModel?.api_base) ||
          (changedModel?.model_type === 'AZURE_OPENAI' && !changedModel?.provider_model)
        ) {
          throw new Error('Please fill in all required fields.');
        }

        const modelId = await addModel({
          model_name: changedModel?.model_name,
          model_type: changedModel?.model_type,
          provider_model: changedModel?.provider_model,
          api_base: changedModel?.api_base,
          api_key: changedModel?.api_key,
        }).unwrap();

        if (setModelAsDefault && models && models.length > 0) {
          await setDefaultModel({ model_id: modelId });
        }

        aysncTestModelWithRetry(modelId);
        setSubmitSuccess(`Model '${changedModel?.model_name}' created successfully!`);
      }

      setIsDrawerOpen(false);
      setSetModelAsDefault(false);
      setSelectedModel(null);
    } catch (error: any) {
      setSubmitError(error.message || 'Failed to save model.');
    }
  };

  const handleTestModel = async (message: string) => {
    if (!selectedModel) return;
    try {
      const response = await testModel({
        model_id: selectedModel.model_id,
        completion_role: 'user',
        completion_content: message,
        temperature: 0.7,
        max_tokens: 50,
        timeout: 3,
      }).unwrap();
      setTestResponse(response);

      // The test passed, set the status to success anyway.
      if (!response.startsWith('Model Test Failed')) {
        setModelTestStatus((prev) => ({ ...prev, [selectedModel.model_id]: 'success' }));
      }
    } catch (error: any) {
      setSubmitError(error.message || 'Failed to test model.');
    }
  };

  useEffect(() => {
    if (searchParams.get('promptNewModelRegistration') === 'true') {
      openCreateModelDrawer();
    }
  }, [searchParams]);

  return (
    <>
      <ModelActionsDrawer
        isOpen={isDrawerOpen}
        onClose={() => {
          setIsDrawerOpen(false);
          setSelectedModel(null);
          setChangedModel(null);
          if (searchParams.get('promptNewModelRegistration')) {
            const newSearchParams = new URLSearchParams(searchParams);
            newSearchParams.delete('promptNewModelRegistration');
            window.history.replaceState(
              {},
              '',
              `${window.location.pathname}${newSearchParams.toString() ? '?' + newSearchParams.toString() : ''}`,
            );
          }
        }}
        drawerMode={drawerMode}
        changedModel={changedModel}
        setChangedModel={setChangedModel}
        selectedModel={selectedModel}
        submitError={submitError}
        submitSuccess={submitSuccess}
        onSubmit={handleFormSubmit}
        onTest={handleTestModel}
        testResponse={testResponse}
        models={models}
        setModelAsDefault={setModelAsDefault}
        onSetModelAsDefaultChange={setSetModelAsDefault}
      />
      <Layout style={{ flex: 1, padding: '16px 24px 22px', flexDirection: 'column' }}>
        <CommonBreadCrumb items={[{ title: 'Language Models' }]} />
        <NoDefaultModelModal />
        <Title level={2} style={{ marginTop: '16px' }}>
          Models
        </Title>
        <Layout
          style={{
            background: 'transparent',
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexGrow: 0,
            padding: '12px 0',
          }}
        >
          {/* Descriptive Text */}
          <Typography.Text style={{ fontWeight: 400, margin: 0 }}>
            Register language models which will be used to build agents and workflows.
          </Typography.Text>

          {/* Register New Model Button */}
          <Button
            type="primary"
            icon={<PlusCircleOutlined />}
            onClick={openCreateModelDrawer}
            style={{ margin: '0 0 0 16px' }}
          >
            Register New Model
          </Button>
        </Layout>
        <ModelList
          models={models!}
          modelTestStatus={modelTestStatus}
          onEdit={openEditModelDrawer}
          onTest={openTestModelDrawer}
          onDelete={async (modelId) => {
            try {
              await removeModel({ model_id: modelId });
              setSubmitSuccess('Model deleted successfully!');
              setModelTestStatus((prev) => {
                const updated = { ...prev };
                delete updated[modelId];
                return updated;
              });
            } catch (error: any) {
              setSubmitError(error.message || 'Failed to delete model.');
            }
          }}
          onSetDefault={async (modelId) => {
            try {
              await setDefaultModel({ model_id: modelId });
              setSubmitSuccess('Default model updated successfully!');
            } catch (error: any) {
              setSubmitError(error.message || 'Failed to set default model.');
            }
          }}
        />
      </Layout>
    </>
  );
};

export default ModelsPage;
