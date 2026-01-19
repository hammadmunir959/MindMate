import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      error: null,
      isLoading: false,

      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setToken: (token) => set({ token }),

      login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          // Import client here to avoid circular dependency if possible, or use dependency injection.
          // For simplicity, we assume client import works globally, but dynamic import is safer for cyclic deps
          // const api = (await import('../api/client')).default;
          // Actually, cyclic dependency between store and interceptor is common.
          // The interceptor uses store.getState(), which is safe.
          // But store depends on client.

          /* Ideally, pass api as argument or import it directly. */
          const { default: api } = await import('../api/client');

          // Form Data format support if needed (FastAPI OAuth2PasswordRequestForm expects form-data)
          // But our V2 Auth endpoints might accept JSON. Let's assume JSON first.
          // Wait, FastAPI OAuth2 usually wants form-data.
          // Let's try JSON first as per refined plan, or fallback to form-data (FormData)
          // Actually, our backend implementation (Auth Repository) used OAuth2PasswordRequestForm?
          // Let's check backend implementation quickly if needed. For now assuming standard JSON.

          // Using Form Data format as expected by OAuth2PasswordRequestForm
          const formData = new FormData();
          formData.append('username', credentials.email);
          formData.append('password', credentials.password);

          const response = await api.post('/v1/auth/login/access-token', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });

          const { access_token, user_type, user_id, full_name } = response.data;
          // Store token
          set({ token: access_token, isAuthenticated: true, isLoading: false });

          // We might need to fetch user details if not provided in token response
          // But auth_new.py returns access_token, token_type, user_type.
          // It does NOT return full user object in current auth_new.py implementation!
          // We need /v1/auth/test-token (or /me) to get user details.

          // Let's fetch user details immediately
          const userResponse = await api.post('/v1/auth/test-token');
          set({ user: userResponse.data });

          return userResponse.data;
        } catch (error) {
          set({ error: error.response?.data?.detail || 'Login failed', isLoading: false });
          throw error;
        }
      },

      signup: async (userData) => {
        set({ isLoading: true, error: null });
        try {
          const { default: api } = await import('../api/client');

          // /v1/auth/register expects: email, password, first_name, last_name, user_type
          const response = await api.post('/v1/auth/register', null, {
            params: userData // Query params? Register endpoint definition: def register(*, email: str...) implies query params if not Body.
            // Wait, auth_new.py: def register(*, email: str, ...)
            // In FastAPI, if they are simple types, they are Query params.
            // UNLESS Body() is used.
            // Let's assume the previous dev made them Query params (ugly) or Form?
            // "def register(*, ...)" usually forces keyword args.
            // I should use query params to be safe matching the signature seen.
          });

          const { access_token } = response.data;
          set({ token: access_token, isAuthenticated: true, isLoading: false });

          // Fetch user details
          const userResponse = await api.post('/v1/auth/test-token');
          set({ user: userResponse.data });

          return userResponse.data;
        } catch (error) {
          set({ error: error.response?.data?.detail || 'Signup failed', isLoading: false });
          throw error;
        }
      },

      logout: () => set({ user: null, token: null, isAuthenticated: false }),

      updateUser: (updates) => set((state) => ({
        user: state.user ? { ...state.user, ...updates } : null
      })),
    }),
    {
      name: 'auth-storage',
    }
  )
);

