import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
    Home as HomeIcon, LogOut, Lightbulb, LightbulbOff,
    StopCircle, AlertTriangle, Trash2, Music
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import SongSelector from '../components/SongSelector';
import Toast from '../components/Toast';
import api from '../services/api';

const Admin = () => {
    const { user, logout } = useAuth();
    const [songs, setSongs] = useState({});
    const [flashMessage, setFlashMessage] = useState('');
    const [queueStatus, setQueueStatus] = useState({
        admin_queue: [],
        requested_queue: [],
        system_queue: [],
        current_song: null
    });

    useEffect(() => {
        loadSongs();
        loadQueueStatus();

        // Poll queue status every 3 seconds
        const interval = setInterval(loadQueueStatus, 3000);
        return () => clearInterval(interval);
    }, []);

    const loadSongs = async () => {
        try {
            const response = await api.get('/songs/list');
            setSongs(response.data.songs);
        } catch (error) {
            console.error('Failed to load songs:', error);
        }
    };

    const loadQueueStatus = async () => {
        try {
            const response = await api.get('/songs/queue');
            setQueueStatus(response.data);
        } catch (error) {
            console.error('Failed to load queue status:', error);
        }
    };

    const showMessage = (message) => {
        setFlashMessage(message);
        setTimeout(() => setFlashMessage(''), 4000);
    };

    const handleAddSong = async (song) => {
        try {
            const response = await api.post('/admin/songs/queue', { song });
            showMessage(response.data.message);
            loadQueueStatus();
        } catch (error) {
            showMessage(error.response?.data?.detail || 'Failed to add song');
        }
    };

    const handleLightsOn = async () => {
        try {
            const response = await api.post('/admin/lights/on');
            showMessage(response.data.message);
        } catch (error) {
            showMessage(error.response?.data?.detail || 'Failed to turn lights on');
        }
    };

    const handleLightsOff = async () => {
        try {
            const response = await api.post('/admin/lights/off');
            showMessage(response.data.message);
        } catch (error) {
            showMessage(error.response?.data?.detail || 'Failed to turn lights off');
        }
    };

    const handleStopSong = async () => {
        try {
            const response = await api.post('/admin/song/stop');
            showMessage(response.data.message);
            loadQueueStatus();
        } catch (error) {
            showMessage(error.response?.data?.detail || 'Failed to stop song');
        }
    };

    const handleClearQueue = async (queueType) => {
        try {
            const response = await api.delete('/admin/queue', {
                data: { queue_type: queueType }
            });
            showMessage(response.data.message);
            loadQueueStatus();
        } catch (error) {
            showMessage(error.response?.data?.detail || 'Failed to clear queue');
        }
    };

    const handleEmergencyShutdown = async () => {
        if (!confirm('Are you sure you want to execute emergency shutdown? This will clear all queues, stop the current song, and turn off lights.')) {
            return;
        }

        try {
            const response = await api.post('/admin/shutdown');
            showMessage(response.data.message);
            loadQueueStatus();
        } catch (error) {
            showMessage(error.response?.data?.detail || 'Failed to execute shutdown');
        }
    };

    const handleLogout = async () => {
        await logout();
        window.location.href = '/';
    };

    return (
        <div className="admin-page">
            {/* Toast Notification */}
            <Toast
                message={flashMessage}
                onClose={() => setFlashMessage('')}
            />

            {/* Navigation */}
            <div className="admin-nav">
                <Link to="/" className="nav-btn">
                    <HomeIcon size={20} />
                    Home
                </Link>
                <div className="nav-spacer" />
                <button onClick={handleLogout} className="nav-btn logout-btn">
                    <LogOut size={20} />
                    Logout
                </button>
            </div>

            <div className="admin-container">
                <div className="admin-header">
                    <h1>Admin Control Panel</h1>
                    <p className="admin-subtitle">Welcome, {user?.name}</p>
                </div>

                {/* Control Buttons */}
                <div className="control-section glass-card">
                    <h2>System Controls</h2>
                    <div className="control-grid">
                        <button onClick={handleLightsOn} className="control-btn btn-lights-on">
                            <Lightbulb size={24} />
                            Lights ON
                        </button>
                        <button onClick={handleLightsOff} className="control-btn btn-lights-off">
                            <LightbulbOff size={24} />
                            Lights OFF
                        </button>
                        <button onClick={handleStopSong} className="control-btn btn-stop">
                            <StopCircle size={24} />
                            Stop Song
                        </button>
                        <button onClick={handleEmergencyShutdown} className="control-btn btn-emergency">
                            <AlertTriangle size={24} />
                            Emergency Shutdown
                        </button>
                    </div>
                </div>

                {/* Queue Status */}
                <div className="queue-section glass-card">
                    <h2>Queue Status</h2>

                    {queueStatus.current_song && (
                        <div className="current-song-admin">
                            <h3>Currently Playing</h3>
                            <div className="song-display">
                                <Music size={20} />
                                <span>{queueStatus.current_song}</span>
                            </div>
                        </div>
                    )}

                    <div className="queue-columns">
                        <div className="queue-column">
                            <div className="queue-header">
                                <h3>Admin Queue ({queueStatus.admin_queue.length})</h3>
                                <button
                                    onClick={() => handleClearQueue('admin')}
                                    className="btn-clear"
                                    disabled={queueStatus.admin_queue.length === 0}
                                >
                                    <Trash2 size={16} />
                                    Clear
                                </button>
                            </div>
                            <div className="queue-list-admin">
                                {queueStatus.admin_queue.length > 0 ? (
                                    queueStatus.admin_queue.map((song, index) => (
                                        <div key={index} className="queue-item">
                                            <span className="queue-num">{index + 1}</span>
                                            <span>{song}</span>
                                        </div>
                                    ))
                                ) : (
                                    <p className="empty-queue-msg">Empty</p>
                                )}
                            </div>
                        </div>

                        <div className="queue-column">
                            <div className="queue-header">
                                <h3>Requested Queue ({queueStatus.requested_queue.length})</h3>
                                <button
                                    onClick={() => handleClearQueue('requested')}
                                    className="btn-clear"
                                    disabled={queueStatus.requested_queue.length === 0}
                                >
                                    <Trash2 size={16} />
                                    Clear
                                </button>
                            </div>
                            <div className="queue-list-admin">
                                {queueStatus.requested_queue.length > 0 ? (
                                    queueStatus.requested_queue.map((song, index) => (
                                        <div key={index} className="queue-item">
                                            <span className="queue-num">{index + 1}</span>
                                            <span>{song}</span>
                                        </div>
                                    ))
                                ) : (
                                    <p className="empty-queue-msg">Empty</p>
                                )}
                            </div>
                        </div>

                        <div className="queue-column">
                            <div className="queue-header">
                                <h3>System Queue ({queueStatus.system_queue.length})</h3>
                                <button
                                    onClick={() => handleClearQueue('system')}
                                    className="btn-clear"
                                    disabled={queueStatus.system_queue.length === 0}
                                >
                                    <Trash2 size={16} />
                                    Clear
                                </button>
                            </div>
                            <div className="queue-list-admin">
                                {queueStatus.system_queue.length > 0 ? (
                                    queueStatus.system_queue.map((song, index) => (
                                        <div key={index} className="queue-item">
                                            <span className="queue-num">{index + 1}</span>
                                            <span>{song}</span>
                                        </div>
                                    ))
                                ) : (
                                    <p className="empty-queue-msg">Empty</p>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Song Selector */}
                <div className="song-selection-admin">
                    <SongSelector
                        songs={songs}
                        onSelect={handleAddSong}
                    />
                </div>
            </div>
        </div>
    );
};

export default Admin;
