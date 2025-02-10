import React from 'react';
import { Modal, Button, Layout, Typography, Form, Input, Upload, Space, Tooltip } from 'antd';
import { UploadOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import Editor from '@monaco-editor/react';

const { TextArea } = Input;

interface WorkflowViewToolModalProps {
  open: boolean;
  onCancel: () => void;
  toolDetails: {
    name: string;
    description: string;
    pythonCode: string;
    pythonRequirements: string;
  };
}

const WorkflowViewToolModal: React.FC<WorkflowViewToolModalProps> = ({
  open,
  onCancel,
  toolDetails,
}) => {
  return (
    <Modal
      open={open}
      title="Tool Details"
      onCancel={onCancel}
      centered
      width="98%"
      style={{ height: '95vh', top: 0 }}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          Cancel
        </Button>,
      ]}
    >
      <div style={{ overflowY: 'auto', height: 'calc(95vh - 108px)' }}>
        <Layout style={{ flex: 1, backgroundColor: '#fff', paddingTop: '16px', overflowY: 'auto' }}>
          <Form layout="vertical">
            <Form.Item
              label={
                <Space>
                  Tool Name
                  <Tooltip title="The name of the tool">
                    <QuestionCircleOutlined style={{ color: '#666' }} />
                  </Tooltip>
                </Space>
              }
            >
              <Input value={toolDetails.name} readOnly />
            </Form.Item>
            <Form.Item
              label={
                <Space>
                  Tool Description
                  <Tooltip title="Detailed description of what the tool does">
                    <QuestionCircleOutlined style={{ color: '#666' }} />
                  </Tooltip>
                </Space>
              }
            >
              <TextArea value={toolDetails.description} readOnly autoSize={{ minRows: 3 }} />
            </Form.Item>
            <Form.Item
              label={
                <Space>
                  tool.py
                  <Tooltip title="The Python code that defines the tool's functionality and interface">
                    <QuestionCircleOutlined style={{ color: '#666' }} />
                  </Tooltip>
                </Space>
              }
            >
              <Editor
                height="200px"
                defaultLanguage="python"
                value={toolDetails.pythonCode || 'N/A'}
                options={{ readOnly: true }}
                theme="vs-dark"
              />
            </Form.Item>
            <Form.Item
              label={
                <Space>
                  requirements.txt
                  <Tooltip title="Python package dependencies required by this tool">
                    <QuestionCircleOutlined style={{ color: '#666' }} />
                  </Tooltip>
                </Space>
              }
            >
              <Editor
                height="200px"
                defaultLanguage="plaintext"
                value={toolDetails.pythonRequirements || 'N/A'}
                options={{ readOnly: true }}
                theme="vs-dark"
              />
            </Form.Item>
          </Form>
        </Layout>
      </div>
    </Modal>
  );
};

export default WorkflowViewToolModal;
