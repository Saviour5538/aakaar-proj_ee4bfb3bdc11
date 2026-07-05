import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Document, Conversation } from '../api/client';
import { getDocuments, getConversations } from '../api/client';

interface ResourceCounts {
  documents: number;
  conversations: number;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [resourceCounts, setResourceCounts] = useState<ResourceCounts>({ documents: 0, conversations: 0 });
  const [recentDocuments, setRecentDocuments] = useState<Document[]>([]);
  const [recentConversations, setRecentConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [documentsResponse, conversationsResponse] = await Promise.all([
          getDocuments(),
          getConversations(),
        ]);

        setResourceCounts({
          documents: documentsResponse.length,
          conversations: conversationsResponse.length,
        });

        setRecentDocuments(documentsResponse.slice(0, 5));
        setRecentConversations(conversationsResponse.slice(0, 5));
      } catch (err) {
        setError('Failed to fetch data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleQuickAction = (action: string) => {
    switch (action) {
      case 'uploadDocument':
        navigate('/documents/upload');
        break;
      case 'newConversation':
        navigate('/conversations/new');
        break;
      default:
        break;
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  if (error) {
    return <div className="flex justify-center items-center h-screen text-red-500">{error}</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Welcome, {user?.name || 'User'}!</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-2">Documents</h2>
          <p className="text-4xl font-bold">{resourceCounts.documents}</p>
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-2">Conversations</h2>
          <p className="text-4xl font-bold">{resourceCounts.conversations}</p>
        </div>
      </div>
      <div className="mb-8">
        <h2 className="text-xl font-bold mb-4">Recent Documents</h2>
        <ul className="bg-white shadow rounded-lg divide-y divide-gray-200">
          {recentDocuments.map((doc) => (
            <li key={doc.id} className="p-4">
              {doc.title}
            </li>
          ))}
        </ul>
      </div>
      <div className="mb-8">
        <h2 className="text-xl font-bold mb-4">Recent Conversations</h2>
        <ul className="bg-white shadow rounded-lg divide-y divide-gray-200">
          {recentConversations.map((conv) => (
            <li key={conv.id} className="p-4">
              {conv.title}
            </li>
          ))}
        </ul>
      </div>
      <div>
        <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => handleQuickAction('uploadDocument')}
            className="bg-blue-500 text-white py-2 px-4 rounded-lg shadow hover:bg-blue-600"
          >
            Upload Document
          </button>
          <button
            onClick={() => handleQuickAction('newConversation')}
            className="bg-green-500 text-white py-2 px-4 rounded-lg shadow hover:bg-green-600"
          >
            Start New Conversation
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;