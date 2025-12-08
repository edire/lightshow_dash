import axios from 'axios';

// In-memory token storage (NOT localStorage!)
let accessToken = null;

export const setAccessToken = (token) => {
    accessToken = token;
};

export const getAccessToken = () => {
    return accessToken;
};

export const clearAccessToken = () => {
    accessToken = null;
};

const api = axios.create({
    baseURL: '/api',
    withCredentials: true,  // Important: Send cookies with requests
});

// Add request interceptor to include access token
api.interceptors.request.use(
    (config) => {
        const token = getAccessToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Add response interceptor for token refresh on 401
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Don't intercept if this IS the refresh endpoint failing
        if (originalRequest.url?.includes('/auth/refresh')) {
            return Promise.reject(error);
        }

        // If unauthorized and we haven't already tried to refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                // Try to refresh token
                // Cookie is sent automatically due to withCredentials: true
                const response = await axios.post('/api/auth/refresh', {}, {
                    withCredentials: true
                });

                const { access_token } = response.data;

                // Store new access token in memory
                setAccessToken(access_token);

                // Retry original request with new token
                originalRequest.headers.Authorization = `Bearer ${access_token}`;
                return api(originalRequest);
            } catch (refreshError) {
                // Refresh failed, redirect to login only if not already on login page
                clearAccessToken();
                if (!window.location.pathname.includes('/login') &&
                    !window.location.pathname.includes('/oauth-callback')) {
                    window.location.href = '/login';
                }
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default api;
