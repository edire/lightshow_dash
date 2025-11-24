import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if user is already authenticated
        const checkAuth = async () => {
            const accessToken = localStorage.getItem('access_token');
            const refreshToken = localStorage.getItem('refresh_token');

            if (!accessToken && !refreshToken) {
                setLoading(false);
                return;
            }

            // If we have a refresh token but no access token, try to refresh
            if (!accessToken && refreshToken) {
                try {
                    const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
                    const { access_token, user_email, user_name, user_picture } = response.data;
                    localStorage.setItem('access_token', access_token);
                    setUser({
                        email: user_email,
                        name: user_name,
                        picture: user_picture
                    });
                } catch (error) {
                    console.error('Failed to refresh token:', error);
                    localStorage.removeItem('refresh_token');
                }
            } else if (accessToken) {
                // Verify the access token is still valid
                try {
                    const response = await api.get('/auth/me');
                    setUser({
                        email: response.data.email,
                        name: response.data.name,
                        picture: response.data.picture
                    });
                } catch (error) {
                    console.error('Failed to verify token:', error);
                    // Token will be refreshed by interceptor if refresh token exists
                }
            }

            setLoading(false);
        };

        checkAuth();
    }, []);

    const login = async () => {
        try {
            const response = await api.get('/auth/login');
            const { authorization_url, state } = response.data;

            // Store state for verification
            localStorage.setItem('oauth_state', state);

            // Redirect to Google OAuth
            window.location.href = authorization_url;
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    };

    const handleCallback = async (code, state) => {
        try {
            const storedState = localStorage.getItem('oauth_state');

            if (state !== storedState) {
                throw new Error('Invalid state parameter');
            }

            const response = await api.post('/auth/callback', { code, state });
            const { access_token, refresh_token, user_email, user_name, user_picture } = response.data;

            localStorage.setItem('access_token', access_token);
            if (refresh_token) {
                localStorage.setItem('refresh_token', refresh_token);
            }
            localStorage.removeItem('oauth_state');

            setUser({
                email: user_email,
                name: user_name,
                picture: user_picture
            });

            return true;
        } catch (error) {
            console.error('Callback handling failed:', error);
            throw error;
        }
    };

    const logout = async () => {
        try {
            await api.post('/auth/logout');
        } catch (error) {
            console.error('Logout request failed:', error);
        } finally {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            setUser(null);
        }
    };

    const value = {
        user,
        loading,
        login,
        logout,
        handleCallback,
        isAuthenticated: !!user
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
