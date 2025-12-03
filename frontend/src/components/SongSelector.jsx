import React, { useState, useMemo } from 'react';
import { Search, Music } from 'lucide-react';

const SongSelector = ({ songs, onSelect }) => {
    const [selectedSong, setSelectedSong] = useState('');
    const [searchTerm, setSearchTerm] = useState('');

    const filteredSongs = useMemo(() => {
        if (!songs) return [];

        const songsArray = Object.entries(songs);
        if (!searchTerm) return songsArray;

        return songsArray.filter(([name]) =>
            name.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }, [songs, searchTerm]);

    const handleConfirm = () => {
        if (selectedSong && onSelect) {
            onSelect(selectedSong);
            setSelectedSong('');
            setSearchTerm('');
        }
    };

    return (
        <div className="song-selector glass-card">
            <div className="song-selector-header">
                <h2>Choose Your Song</h2>
                <p className="subtitle">Select from our collection of holiday favorites</p>
            </div>

            <div className="search-box">
                <Search size={20} />
                <input
                    type="text"
                    placeholder="Search songs..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="search-input"
                />
            </div>

            <div className="songs-grid">
                {filteredSongs.map(([songName, songFile]) => (
                    <div
                        key={songName}
                        className={`song-card ${selectedSong === songName ? 'selected' : ''}`}
                        onClick={() => setSelectedSong(songName)}
                    >
                        <Music size={24} />
                        <span className="song-name">{songName}</span>
                    </div>
                ))}
            </div>

            {filteredSongs.length === 0 && (
                <div className="no-results">
                    <Music size={48} />
                    <p>No songs found</p>
                </div>
            )}

            <button
                onClick={handleConfirm}
                disabled={!selectedSong}
                className="btn-primary"
            >
                Add to Queue
            </button>
        </div>
    );
};

export default SongSelector;
