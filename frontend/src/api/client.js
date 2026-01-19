import axios from 'axios';
import { useAuthStore } from '../stores/authStore';

const apiClient = axios.create({
    baseURL: 'http://localhost:8000/api', // V2 Backend URL
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request Interceptor: Inject Token
apiClient.interceptors.request.use(
    (config) => {
        // Get token from Zustand store
        // Note: getState() is the non-hook way to access store
        const token = useAuthStore.getState().token;

        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response Interceptor: Handle 401 (Logout)
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            // Auto-logout on token expiration
            useAuthStore.getState().logout();
        }
        return Promise.reject(error);
    }
);

export default apiClient;
