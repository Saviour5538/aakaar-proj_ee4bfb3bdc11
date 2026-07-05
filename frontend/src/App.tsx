import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import DocumentsList from './pages/DocumentsList';
import DocumentsForm from './pages/DocumentsForm';
import ConversationsList from './pages/ConversationsList';
import ConversationsForm from './pages/ConversationsForm';
import Chat from './pages/Chat';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/documents" element={<DocumentsList />} />
            <Route path="/documents/new" element={<DocumentsForm />} />
            <Route path="/conversations" element={<ConversationsList />} />
            <Route path="/conversations/new" element={<ConversationsForm />} />
            <Route path="/chat" element={<Chat />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;