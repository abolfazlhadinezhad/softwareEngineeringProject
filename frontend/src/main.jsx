import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './features/auth/AuthProvider';
import App from './App';
import './styles.css';

const client = new QueryClient({ defaultOptions: { queries: { retry: 1, staleTime: 0, gcTime: 300000 } } });
createRoot(document.getElementById('root')).render(<React.StrictMode><QueryClientProvider client={client}><BrowserRouter><AuthProvider><App /></AuthProvider></BrowserRouter></QueryClientProvider></React.StrictMode>);
