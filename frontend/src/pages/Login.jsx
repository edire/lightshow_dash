import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LogIn } from 'lucide-react';

const Login = () => {
    const { login } = useAuth();
    const [loading, setLoading] = React.useState(false);

    const handleLogin = async () => {
        setLoading(true);
        try {
            await login();
        } catch (error) {
            console.error('Login failed:', error);
            setLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="login-container">
                <div className="login-card glass-card">
                    <div className="login-header">
                        <div className="icon-header">
                            <span className="sparkle">✨</span>
                            <span className="tree">🎄</span>
                            <span className="sparkle">✨</span>
                        </div>
                        <h1 className="login-title">Christmas Lightshow</h1>
                        <p className="login-subtitle">Admin Access</p>
                    </div>

                    <div className="login-content">
                        <p className="login-description">
                            Sign in with your authorized Google account to access the admin dashboard
                        </p>

                        <button
                            onClick={handleLogin}
                            disabled={loading}
                            className="btn-google"
                        >
                            <LogIn size={20} />
                            {loading ? 'Signing in...' : 'Sign in with Google'}
                        </button>
                    </div>

                    <div className="login-footer">
                        <a href="/" className="link-home">← Back to Home</a>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
