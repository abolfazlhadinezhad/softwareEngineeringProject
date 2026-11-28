import { createContext, useContext } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../../services/api';

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const client = useQueryClient();
  const session = useQuery({
    queryKey: ['session'],
    retry: false,
    refetchInterval: 60000,
    queryFn: async () => {
      try {
        return await api('/auth/me/');
      } catch (error) {
        if (error.status === 403) {
          client.removeQueries({
            predicate: (q) => !['session', 'public'].includes(q.queryKey[0]),
          });
          return null;
        }
        throw error;
      }
    },
  });
  const signIn = async (credentials) => {
    const user = await api('/auth/login/', { method: 'POST', body: credentials });
    await client.cancelQueries({
      predicate: (query) => !['session', 'public'].includes(query.queryKey[0]),
    });
    client.removeQueries({
      predicate: (query) => !['session', 'public'].includes(query.queryKey[0]),
    });
    client.setQueryData(['session'], user);
    return user;
  };
  const signOut = async () => {
    await api('/auth/logout/', { method: 'POST' });
    await client.cancelQueries({
      predicate: (query) => !['session', 'public'].includes(query.queryKey[0]),
    });
    client.removeQueries({
      predicate: (query) => !['session', 'public'].includes(query.queryKey[0]),
    });
    client.setQueryData(['session'], null);
  };
  return (
    <AuthContext.Provider
      value={{
        user: session.data,
        isLoading: session.isPending,
        error: session.error,
        retry: session.refetch,
        signIn,
        signOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
