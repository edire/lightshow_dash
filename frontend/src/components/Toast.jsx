import React, { useEffect } from 'react';

const Toast = ({ message, onClose, duration = 4000 }) => {
    useEffect(() => {
        if (message) {
            const timer = setTimeout(() => {
                onClose();
            }, duration);

            return () => clearTimeout(timer);
        }
    }, [message, duration, onClose]);

    if (!message) return null;

    return (
        <div className="toast-container">
            <div className="toast">
                {message}
            </div>
        </div>
    );
};

export default Toast;
