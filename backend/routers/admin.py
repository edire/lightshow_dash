from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Literal

from backend.dependencies import get_current_user
from backend.utils.queueing import song_queue_manager
from backend.utils import fpp_commands

router = APIRouter()


class AdminSongRequest(BaseModel):
    song: str


class ClearQueueRequest(BaseModel):
    queue_type: Literal["admin", "requested", "system", "all"]


@router.post("/songs/queue")
async def add_to_admin_queue(
    request: AdminSongRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Add a song to the admin queue (bypasses time restrictions).
    Requires authentication.
    """
    if not request.song:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No song selected"
        )
    
    try:
        song_queue_manager.add_song(request.song, "admin")
        return {
            "message": f"Song '{request.song}' added to admin queue",
            "song": request.song
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add song: {str(e)}"
        )


@router.delete("/queue")
async def clear_queue(
    request: ClearQueueRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Clear a specific queue or all queues.
    Requires authentication.
    """
    try:
        if request.queue_type == "all":
            song_queue_manager.clear_queues()
            return {"message": "All queues cleared"}
        else:
            # Clear specific queue
            with song_queue_manager.lock:
                if request.queue_type == "admin":
                    song_queue_manager.admin_queue.clear()
                elif request.queue_type == "requested":
                    song_queue_manager.requested_queue.clear()
                elif request.queue_type == "system":
                    song_queue_manager.system_queue.clear()
            
            return {"message": f"{request.queue_type.capitalize()} queue cleared"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear queue: {str(e)}"
        )


@router.post("/lights/on")
async def turn_lights_on(current_user: dict = Depends(get_current_user)):
    """
    Turn lights on.
    Requires authentication.
    """
    try:
        fpp_commands.lights_on()
        return {"message": "Lights turned on"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to turn lights on: {str(e)}"
        )


@router.post("/lights/off")
async def turn_lights_off(current_user: dict = Depends(get_current_user)):
    """
    Turn lights off.
    Requires authentication.
    """
    try:
        fpp_commands.lights_off()
        return {"message": "Lights turned off"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to turn lights off: {str(e)}"
        )


@router.post("/song/stop")
async def stop_current_song(current_user: dict = Depends(get_current_user)):
    """
    Stop the current song.
    Requires authentication.
    """
    try:
        fpp_commands.stop_song()
        song_queue_manager.set_current_song(None)
        return {"message": "Song stopped"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop song: {str(e)}"
        )


@router.post("/shutdown")
async def emergency_shutdown(current_user: dict = Depends(get_current_user)):
    """
    Emergency shutdown: clear all queues, stop song, turn off lights.
    Requires authentication.
    """
    try:
        song_queue_manager.clear_queues()
        fpp_commands.stop_song()
        fpp_commands.lights_off()
        song_queue_manager.set_current_song(None)
        return {"message": "Emergency shutdown complete"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute shutdown: {str(e)}"
        )
