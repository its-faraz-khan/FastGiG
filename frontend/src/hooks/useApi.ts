import { useState, useCallback } from 'react';
import { AxiosError } from 'axios';
import apiClient from '@/services/apiClient';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: AxiosError | null;
}

export const useApi = <T,>(initialData: T | null = null) => {
  const [state, setState] = useState<UseApiState<T>>({
    data: initialData,
    loading: false,
    error: null,
  });

  const execute = useCallback(
    async (method: 'get' | 'post' | 'put' | 'delete', url: string, payload?: unknown) => {
      setState({ data: null, loading: true, error: null });
      try {
        const response = await apiClient[method]<T>(url, payload);
        setState({ data: response.data, loading: false, error: null });
        return response.data;
      } catch (error) {
        const axiosError = error as AxiosError;
        setState({ data: null, loading: false, error: axiosError });
        throw axiosError;
      }
    },
    []
  );

  return { ...state, execute };
};
