'use client';

import React from 'react';
import AgentForm from '@/app/components/AgentForm';
import { useParams } from 'next/navigation';

const EditAgentPage: React.FC = () => {
  const { id } = useParams(); // Get the dynamic `id` from the route

  // Ensure `id` is a string or undefined
  const agentId = Array.isArray(id) ? id[0] : id;

  return <AgentForm agentTemplateId={agentId} />;
};

export default EditAgentPage;
