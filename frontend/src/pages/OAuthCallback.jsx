import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const OAuthCallback = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const { handleCallback } = useAuth();
    const [error, setError] = React.useState(null);

    const processedRef = React.useRef(false);

    useEffect(() => {
        const processCallback = async () => {
            // Prevent double execution
            if (processedRef.current) return;
            processedRef.current = true;

            const code = searchParams.get('code');
            const state = searchParams.get('state');
            const errorParam = searchParams.get('error');

            if (errorParam) {
                setError(`Authentication failed: ${errorParam}`);
                setTimeout(() => navigate('/login'), 3000);
                return;
            }

            if (!code || !state) {
                setError('Missing required parameters');
                setTimeout(() => navigate('/login'), 3000);
                return;
            }

            try {
                await handleCallback(code, state);
                // Redirect to admin page after successful authentication
                navigate('/admin');
            } catch (err) {
                console.error('Callback error:', err);
                setError(err.message || 'Authentication failed');
                setTimeout(() => navigate('/login'), 3000);
            }
        };

        processCallback();
    }, [searchParams, handleCallback, navigate]);

    return (
        <div className="callback-container">
            <div className="callback-content">
                {error ? (
                    <>
                        <div className="error-icon">✕</div>
                        <h2>Authentication Error</h2>
                        <p>{error}</p>
                        <p className="redirect-message">Redirecting to login...</p>
                    </>
                ) : (
                    <>
                        <div className="spinner"></div>
                        <h2>Completing Authentication</h2>
                        <p>Please wait while we sign you in...</p>
                    </>
                )}
            </div>
        </div>
    );
};

export default OAuthCallback;
