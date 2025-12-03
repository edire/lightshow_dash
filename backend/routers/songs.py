from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import os
import datetime as dt
import httpx

from backend.utils.queueing import song_queue_manager, get_song_list, check_time

router = APIRouter()


class SongRequest(BaseModel):
    song: str


class CustomSongRequest(BaseModel):
    request_text: str


class QueueStatus(BaseModel):
    admin_queue: List[str]
    requested_queue: List[str]
    system_queue: List[str]
    current_song: Optional[str]


@router.get("/list")
async def get_songs():
    """Get the list of available songs."""
    try:
        songs = get_song_list()
        return {"songs": songs}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load songs: {str(e)}"
        )


@router.get("/queue", response_model=QueueStatus)
async def get_queue_status():
    """Get current queue status for all queues."""
    try:
        return QueueStatus(
            admin_queue=song_queue_manager.peek_queues("admin") or [],
            requested_queue=song_queue_manager.peek_queues("requested") or [],
            system_queue=song_queue_manager.peek_queues("system") or [],
            current_song=song_queue_manager.get_current_song()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get queue status: {str(e)}"
        )


@router.post("/request")
async def request_song(request: SongRequest):
    """
    Request a song to be added to the queue (public endpoint).
    Songs can only be requested during allowed hours.
    """
    if not request.song:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No song selected"
        )
    
    # Check if within allowed time
    if not check_time():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Current time is outside the allowed range of 5:00 PM - 8:30 PM"
        )
    
    try:
        # Add to requested queue
        song_queue_manager.add_song(request.song, "requested")
        
        # Log the request
        with open('song_requests.txt', 'a') as f:
            timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} - {request.song}\n")
        
        return {
            "message": f"Your song '{request.song}' has been added to the queue!",
            "song": request.song
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add song to queue: {str(e)}"
        )


@router.post("/request-custom")
async def submit_custom_request(request: CustomSongRequest):
    """
    Submit a custom song request via email.
    """
    if not request.request_text or not request.request_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request text cannot be empty"
        )
    
    try:
        # Send to N8N webhook
        webhook_url = os.getenv('N8N_WEBHOOK_URL')
        token = os.getenv('N8N_TOKEN')

        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json={
                    "subject": "LightshowPi Song Request",
                    "request": request.request_text
                },
                headers={
                    "Authorization": f"Bearer {token}"
                }
            )
            response.raise_for_status()

        return {
            "message": "Your request has been submitted. Please check back at a later date."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit request: {str(e)}"
        )
