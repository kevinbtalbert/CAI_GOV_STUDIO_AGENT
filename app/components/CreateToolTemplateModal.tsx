import React, { useState } from 'react';
import { Modal, Input } from 'antd';

interface CreateToolTemplateModalProps {
  isOpen: boolean;
  onCancel: () => void;
  onGenerate: (toolName: string) => void;
}

const CreateToolTemplateModal: React.FC<CreateToolTemplateModalProps> = ({
  isOpen,
  onCancel,
  onGenerate,
}) => {
  const [toolName, setToolName] = useState('');

  const handleGenerate = () => {
    if (toolName.trim()) {
      onGenerate(toolName.trim());
      setToolName('');
    }
  };

  return (
    <Modal
      title="Create Tool Template"
      open={isOpen}
      onCancel={onCancel}
      onOk={handleGenerate}
      okText="Generate"
      cancelText="Cancel"
    >
      <div style={{ marginTop: '16px' }}>
        <Input
          placeholder="Enter Tool Name"
          value={toolName}
          onChange={(e) => setToolName(e.target.value)}
          onPressEnter={handleGenerate}
          style={{
            marginTop: '16px',
            marginBottom: '16px',
            padding: '8px 12px',
            borderRadius: '4px',
          }}
        />
      </div>
    </Modal>
  );
};

export default CreateToolTemplateModal;
