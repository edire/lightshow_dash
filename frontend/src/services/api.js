import axios from 'axios';

const api = axios.create({
    baseURL: '/api',
    withCredentials: true,
});

// Add request interceptor to include access token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Add response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // If unauthorized and we have a refresh token, try to refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
                try {
                    const response = await axios.post('/api/auth/refresh', {
                        refresh_token: refreshToken
                    });

                    const { access_token, refresh_token: newRefreshToken } = response.data;
                    localStorage.setItem('access_token', access_token);
                    if (newRefreshToken) {
                        localStorage.setItem('refresh_token', newRefreshToken);
                    }

                    // Retry original request with new token
                    originalRequest.headers.Authorization = `Bearer ${access_token}`;
                    return api(originalRequest);
                } catch (refreshError) {
                    // Refresh failed, clear tokens and redirect to login
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    window.location.href = '/login';
                    return Promise.reject(refreshError);
                }
            }
        }

        return Promise.reject(error);
    }
);

export default api;
