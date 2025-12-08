import React, { createContext, useContext, useState, useEffect } from 'react';
import api, { setAccessToken, clearAccessToken } from '../services/api';

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
        // On initial load, try to refresh token using HttpOnly cookie
        const checkAuth = async () => {
            // Skip if we're on the login or callback pages
            if (window.location.pathname.includes('/login') ||
                window.location.pathname.includes('/oauth-callback')) {
                setLoading(false);
                return;
            }

            try {
                // Attempt to refresh - cookie is sent automatically
                const response = await api.post('/auth/refresh');
                const { access_token } = response.data;

                // Store in memory
                setAccessToken(access_token);

                // Get user info
                const userResponse = await api.get('/auth/me');
                setUser({
                    email: userResponse.data.email,
                    name: userResponse.data.name,
                    picture: userResponse.data.picture || ''
                });
            } catch (error) {
                // No valid session, user needs to login
                console.log('No active session');
                clearAccessToken();
            } finally {
                setLoading(false);
            }
        };

        checkAuth();
    }, []);

    const login = async () => {
        try {
            // Get login URL from backend
            const response = await api.get('/auth/login-url');
            const { url } = response.data;

            // Redirect to Google OAuth
            window.location.href = url;
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    };

    const handleCallback = async (code) => {
        try {
            // Exchange code for tokens
            const response = await api.get(`/auth/callback?code=${code}`);
            const { access_token, user: userData } = response.data;

            // Store access token in memory
            setAccessToken(access_token);

            // Set user data
            setUser({
                email: userData.email,
                name: userData.name,
                picture: userData.picture || ''
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
            // Clear in-memory token
            clearAccessToken();
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
