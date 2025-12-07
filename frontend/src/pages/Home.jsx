import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, TreePine, Clock, Send, ShieldCheck } from 'lucide-react';
import SongSelector from '../components/SongSelector';
import Toast from '../components/Toast';
import api from '../services/api';

const Home = () => {
    const [songs, setSongs] = useState({});
    const [flashMessage, setFlashMessage] = useState('');
    const [queueStatus, setQueueStatus] = useState({
        admin_queue: [],
        requested_queue: [],
        system_queue: [],
        current_song: null
    });
    const [songRequestText, setSongRequestText] = useState('');
    const [bannerContent, setBannerContent] = useState(null);

    useEffect(() => {
        loadSongs();
        loadQueueStatus();
        loadBanner();

        // Poll queue status every 5 seconds
        const interval = setInterval(loadQueueStatus, 5000);
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

    const loadBanner = async () => {
        try {
            const response = await api.get('/banner');
            setBannerContent(response.data.content);
        } catch (error) {
            console.error('Failed to load banner:', error);
        }
    };

    const handleSongSelect = async (song) => {
        try {
            const response = await api.post('/songs/request', { song });
            setFlashMessage(response.data.message);
            loadQueueStatus();

            // Clear flash message after 5 seconds
            setTimeout(() => setFlashMessage(''), 5000);
        } catch (error) {
            const message = error.response?.data?.detail || 'Failed to add song to queue';
            setFlashMessage(message);
            setTimeout(() => setFlashMessage(''), 5000);
        }
    };

    const handleSubmitRequest = async () => {
        if (!songRequestText.trim()) {
            setFlashMessage('Please enter a song request');
            setTimeout(() => setFlashMessage(''), 3000);
            return;
        }

        try {
            const response = await api.post('/songs/request-custom', {
                request_text: songRequestText
            });
            setFlashMessage(response.data.message);
            setSongRequestText('');
            setTimeout(() => setFlashMessage(''), 5000);
        } catch (error) {
            const message = error.response?.data?.detail || 'Failed to submit request';
            setFlashMessage(message);
            setTimeout(() => setFlashMessage(''), 5000);
        }
    };

    const combinedQueue = [
        ...queueStatus.admin_queue,
        ...queueStatus.requested_queue
    ];

    return (
        <div className="page-container">
            {/* Toast Notification */}
            <Toast
                message={flashMessage}
                onClose={() => setFlashMessage('')}
            />

            {/* Admin Button */}
            <Link to="/admin" className="admin-link">
                <button className="btn-ghost">
                    <ShieldCheck size={20} />
                    Admin
                </button>
            </Link>

            <div className="content-wrapper">
                {/* Hero Section */}
                <div className="hero-section">
                    <div className="hero-content">
                        <div className="icon-header">
                            <Sparkles size={48} className="sparkle-icon" />
                            <TreePine size={64} className="tree-icon" />
                            <Sparkles size={48} className="sparkle-icon" />
                        </div>

                        <h1 className="hero-title">Linda Ln Christmas Lightshow</h1>

                        <div className="time-badge">
                            <Clock size={20} />
                            <span>Available 5:00 PM - 8:30 PM</span>
                        </div>
                    </div>
                </div>

                {/* Banner */}
                {bannerContent && (
                    <div className="banner-section">
                        <div className="banner-content">
                            {bannerContent.split('\n').map((line, index) => (
                                <p key={index}>{line}</p>
                            ))}
                        </div>
                    </div>
                )}

                {/* Song Selection */}
                <div className="song-selection-section">
                    <SongSelector
                        songs={songs}
                        onSelect={handleSongSelect}
                    />
                </div>

                {/* Queue Status */}
                <div className="queue-status-section">
                    <div className="glass-card">
                        <h2>Live Queue Status</h2>

                        {queueStatus.current_song && (
                            <div className="current-song">
                                <h3>Now Playing</h3>
                                <div className="song-item playing">
                                    <TreePine size={20} />
                                    <span>{queueStatus.current_song}</span>
                                </div>
                            </div>
                        )}

                        {combinedQueue.length > 0 ? (
                            <div className="queue-list">
                                <h3>Up Next ({combinedQueue.length})</h3>
                                {combinedQueue.slice(0, 5).map((song, index) => (
                                    <div key={index} className="song-item">
                                        <span className="queue-number">{index + 1}</span>
                                        <span>{song}</span>
                                    </div>
                                ))}
                                {combinedQueue.length > 5 && (
                                    <p className="more-songs">+ {combinedQueue.length - 5} more songs</p>
                                )}
                            </div>
                        ) : (
                            !queueStatus.current_song && (
                                <div className="empty-queue">
                                    <TreePine size={48} />
                                    <p>No songs in queue. Be the first to add one!</p>
                                </div>
                            )
                        )}
                    </div>
                </div>

                {/* Request a New Song Section */}
                <div className="request-section">
                    <div className="glass-card">
                        <h2>Request a New Song</h2>
                        <p className="subtitle">
                            Don't see your favorite song? Request it and we'll add it to our playlist!
                        </p>

                        <textarea
                            placeholder="Enter song name and your email..."
                            value={songRequestText}
                            onChange={(e) => setSongRequestText(e.target.value)}
                            className="request-textarea"
                            rows={4}
                        />

                        <button onClick={handleSubmitRequest} className="btn-primary">
                            <Send size={20} />
                            Submit Request
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home;
