
import reflex as rx
import utils.fpp_commands as fpp
from typing import List
from utils.gauth import AuthState, require_auth
from utils.ui_components import song_selector
import utils.queueing as queueing


# Import the song queue manager from index_page to share state
from app.page_index import song_queue_manager


class AdminState(rx.State):
    flash_message: str = ""
    admin_queue: List[str] = []
    requested_queue: List[str] = []
    system_queue: List[str] = []
    current_song: str = ""
    songs: dict = {}
    selected_song: str = ""
    song_flash_message: str = ""

    def on_load(self):
        """Load initial data when page loads."""
        try:
            self.songs = queueing.get_song_list()
            self.update_status()
        except:
            pass

    def update_status(self):
        """Update the current status of queues and song."""
        self.admin_queue = song_queue_manager.peek_queues('admin') or []
        self.requested_queue = song_queue_manager.peek_queues('requested') or []
        self.system_queue = song_queue_manager.peek_queues('system') or []
        self.current_song = song_queue_manager.get_current_song() or "No song playing"

    def lights_on_action(self):
        """Turn lights on."""
        fpp.lights_on()
        self.flash_message = "Lights turned ON"
        self.update_status()

    def lights_off_action(self):
        """Turn lights off."""
        fpp.lights_off()
        self.flash_message = "Lights turned OFF"
        self.update_status()

    def stop_song_action(self):
        """Stop the current song."""
        fpp.stop_song()
        self.flash_message = "Current song stopped"
        self.update_status()

    def shut_down_all_action(self):
        """Emergency shutdown: clear all queues, stop song, turn off lights."""
        song_queue_manager.clear_queues()
        fpp.stop_song()
        fpp.lights_off()
        self.flash_message = "EMERGENCY SHUTDOWN: All queues cleared, song stopped, lights off"
        self.update_status()

    def clear_admin_queue_action(self):
        """Clear only the admin queue."""
        with song_queue_manager.lock:
            song_queue_manager.admin_queue.clear()
        self.flash_message = "Admin queue cleared"
        self.update_status()

    def clear_requested_queue_action(self):
        """Clear only the requested queue."""
        with song_queue_manager.lock:
            song_queue_manager.requested_queue.clear()
        self.flash_message = "Requested queue cleared"
        self.update_status()

    def clear_system_queue_action(self):
        """Clear only the system queue."""
        with song_queue_manager.lock:
            song_queue_manager.system_queue.clear()
        self.flash_message = "System queue cleared"
        self.update_status()

    def set_selected_song(self, song: str):
        """Set the selected song."""
        self.selected_song = song

    def choose_song(self):
        """Add selected song to admin queue."""
        if not self.selected_song:
            self.song_flash_message = "No song selected. Please choose a song."
            return
        song_queue_manager.add_song(self.selected_song, "admin")
        self.song_flash_message = f"Song '{self.selected_song}' has been added to the admin queue!"
        self.update_status()
        self.selected_song = ""


@rx.page(route="/admin", on_load=[AdminState.on_load])
# @rx.page(route="/admin", on_load=[AuthState.check_auth, AdminState.on_load])
# @require_auth
def admin() -> rx.Component:
    """Admin control panel page."""
    return rx.container(
            rx.vstack(
                # Header
                rx.heading(
                    "Admin Control Panel",
                    font_size="3rem",
                    color="#d32f2f",
                    text_align="center",
                    margin_bottom="20px",
                    font_weight="bold",
                    letter_spacing="2px",
                ),
                rx.text(
                    "Linda Ln Christmas Lightshow Administration",
                    color="#333",
                    text_align="center",
                    margin_bottom="10px",
                    font_size="1.2rem",
                ),
                rx.text(
                    "Logged in as: " + AuthState.user_email,
                    color="#666",
                    text_align="center",
                    margin_bottom="20px",
                    font_size="0.9rem",
                    font_style="italic",
                ),

                # Flash Message
                rx.cond(
                    AdminState.flash_message != "",
                    rx.box(
                        rx.text(
                            AdminState.flash_message,
                            color="#cc201a",
                            text_align="center",
                            font_size="18px",
                            font_weight="bold",
                        ),
                        max_width="800px",
                        margin="20px auto",
                        padding="15px",
                        background_color="#fff3cd",
                        border_radius="8px",
                        border="2px solid #ffc107",
                    ),
                ),

                # Current Status Box
                rx.box(
                    rx.vstack(
                        rx.heading(
                            "Current Status",
                            font_size="1.8rem",
                            color="#333",
                            margin_bottom="15px",
                        ),
                        rx.text(
                            "Currently Playing: " + AdminState.current_song,
                            font_size="1.1rem",
                            color="#555",
                            font_weight="bold",
                        ),
                        rx.button(
                            "Refresh Status",
                            on_click=AdminState.update_status,
                            background_color="#2196f3",
                            color="#fff",
                            padding="10px 20px",
                            border_radius="5px",
                            _hover={"background_color": "#1976d2"},
                            cursor="pointer",
                            margin_top="10px",
                        ),
                        spacing="3",
                    ),
                    width="100%",
                    max_width="800px",
                    margin="0 auto 30px auto",
                    padding="25px",
                    background_color="#e3f2fd",
                    border_radius="10px",
                    box_shadow="0 0 20px rgba(0, 0, 0, 0.1)",
                    border="2px solid #2196f3",
                ),

                # Song Selection
                rx.box(
                    song_selector(
                        songs_dict=AdminState.songs,
                        selected_song=AdminState.selected_song,
                        on_song_change=AdminState.set_selected_song,
                        on_confirm=AdminState.choose_song,
                        flash_message=AdminState.song_flash_message,
                        heading="Add Song to Admin Queue",
                    ),
                    width="100%",
                    max_width="800px",
                    margin="0 auto 30px auto",
                    padding="25px",
                    background_color="#fff",
                    border_radius="10px",
                    box_shadow="0 0 20px rgba(0, 0, 0, 0.1)",
                    border="2px solid #ccc",
                ),

                # Primary Controls
                rx.box(
                    rx.vstack(
                        rx.heading(
                            "Primary Controls",
                            font_size="1.8rem",
                            color="#333",
                            margin_bottom="15px",
                        ),
                        rx.hstack(
                            rx.button(
                                "💡 Lights ON",
                                on_click=AdminState.lights_on_action,
                                width="200px",
                                height="80px",
                                font_size="20px",
                                background_color="#4caf50",
                                color="#fff",
                                border_radius="8px",
                                font_weight="bold",
                                _hover={"background_color": "#45a049"},
                                cursor="pointer",
                            ),
                            rx.button(
                                "🌙 Lights OFF",
                                on_click=AdminState.lights_off_action,
                                width="200px",
                                height="80px",
                                font_size="20px",
                                background_color="#ff9800",
                                color="#fff",
                                border_radius="8px",
                                font_weight="bold",
                                _hover={"background_color": "#e68900"},
                                cursor="pointer",
                            ),
                            rx.button(
                                "⏹️ Stop Song",
                                on_click=AdminState.stop_song_action,
                                width="200px",
                                height="80px",
                                font_size="20px",
                                background_color="#f44336",
                                color="#fff",
                                border_radius="8px",
                                font_weight="bold",
                                _hover={"background_color": "#da190b"},
                                cursor="pointer",
                            ),
                            spacing="4",
                            flex_wrap="wrap",
                            justify="center",
                        ),
                        spacing="4",
                    ),
                    width="100%",
                    max_width="800px",
                    margin="0 auto 30px auto",
                    padding="25px",
                    background_color="#fff",
                    border_radius="10px",
                    box_shadow="0 0 20px rgba(0, 0, 0, 0.1)",
                    border="2px solid #ccc",
                ),

                # Emergency Control
                rx.box(
                    rx.vstack(
                        rx.heading(
                            "⚠️ Emergency Controls",
                            font_size="1.8rem",
                            color="#d32f2f",
                            margin_bottom="15px",
                        ),
                        rx.text(
                            "Warning: This will clear ALL queues, stop current song, and turn off lights",
                            color="#666",
                            font_style="italic",
                            text_align="center",
                            margin_bottom="10px",
                        ),
                        rx.button(
                            "🚨 SHUT DOWN ALL 🚨",
                            on_click=AdminState.shut_down_all_action,
                            width="100%",
                            height="80px",
                            font_size="24px",
                            background_color="#b71c1c",
                            color="#fff",
                            border_radius="8px",
                            font_weight="bold",
                            _hover={"background_color": "#8b0000"},
                            cursor="pointer",
                        ),
                        spacing="3",
                    ),
                    width="100%",
                    max_width="800px",
                    margin="0 auto 30px auto",
                    padding="25px",
                    background_color="#ffebee",
                    border_radius="10px",
                    box_shadow="0 0 20px rgba(0, 0, 0, 0.1)",
                    border="3px solid #d32f2f",
                ),

                # Queue Management
                rx.box(
                    rx.vstack(
                        rx.heading(
                            "Queue Management",
                            font_size="1.8rem",
                            color="#333",
                            margin_bottom="15px",
                        ),

                        # Admin Queue
                        rx.vstack(
                            rx.hstack(
                                rx.text(
                                    "Admin Queue (" + AdminState.admin_queue.length().to(str) + ")",
                                    font_size="1.2rem",
                                    font_weight="bold",
                                    color="#d32f2f",
                                ),
                                rx.button(
                                    "Clear Admin Queue",
                                    on_click=AdminState.clear_admin_queue_action,
                                    size="2",
                                    background_color="#d32f2f",
                                    color="#fff",
                                    _hover={"background_color": "#b71c1c"},
                                ),
                                justify="between",
                                width="100%",
                            ),
                            rx.box(
                                rx.list(
                                    rx.foreach(
                                        AdminState.admin_queue,
                                        lambda song: rx.list_item(
                                            song,
                                            background_color="#ffebee",
                                            margin="5px 0",
                                            padding="10px",
                                            border_radius="5px",
                                        ),
                                    ),
                                ),
                                max_height="150px",
                                overflow_y="auto",
                                width="100%",
                            ),
                            spacing="2",
                            width="100%",
                        ),

                        # Requested Queue
                        rx.vstack(
                            rx.hstack(
                                rx.text(
                                    "Requested Queue (" + AdminState.requested_queue.length().to(str) + ")",
                                    font_size="1.2rem",
                                    font_weight="bold",
                                    color="#2196f3",
                                ),
                                rx.button(
                                    "Clear Requested Queue",
                                    on_click=AdminState.clear_requested_queue_action,
                                    size="2",
                                    background_color="#2196f3",
                                    color="#fff",
                                    _hover={"background_color": "#1976d2"},
                                ),
                                justify="between",
                                width="100%",
                            ),
                            rx.box(
                                rx.list(
                                    rx.foreach(
                                        AdminState.requested_queue,
                                        lambda song: rx.list_item(
                                            song,
                                            background_color="#e3f2fd",
                                            margin="5px 0",
                                            padding="10px",
                                            border_radius="5px",
                                        ),
                                    ),
                                ),
                                max_height="150px",
                                overflow_y="auto",
                                width="100%",
                            ),
                            spacing="2",
                            width="100%",
                        ),

                        # System Queue
                        rx.vstack(
                            rx.hstack(
                                rx.text(
                                    "System Queue (" + AdminState.system_queue.length().to(str) + ")",
                                    font_size="1.2rem",
                                    font_weight="bold",
                                    color="#4caf50",
                                ),
                                rx.button(
                                    "Clear System Queue",
                                    on_click=AdminState.clear_system_queue_action,
                                    size="2",
                                    background_color="#4caf50",
                                    color="#fff",
                                    _hover={"background_color": "#45a049"},
                                ),
                                justify="between",
                                width="100%",
                            ),
                            rx.box(
                                rx.list(
                                    rx.foreach(
                                        AdminState.system_queue,
                                        lambda song: rx.list_item(
                                            song,
                                            background_color="#e8f5e9",
                                            margin="5px 0",
                                            padding="10px",
                                            border_radius="5px",
                                        ),
                                    ),
                                ),
                                max_height="150px",
                                overflow_y="auto",
                                width="100%",
                            ),
                            spacing="2",
                            width="100%",
                        ),

                        spacing="5",
                    ),
                    width="100%",
                    max_width="800px",
                    margin="0 auto",
                    padding="25px",
                    background_color="#fff",
                    border_radius="10px",
                    box_shadow="0 0 20px rgba(0, 0, 0, 0.1)",
                    border="2px solid #ccc",
                ),

                # Back to home link and logout
                rx.hstack(
                    rx.link(
                        "← Back to Home",
                        href="/",
                        color="#2196f3",
                        font_size="1.1rem",
                        _hover={"text_decoration": "underline"},
                    ),
                    rx.button(
                        "Logout",
                        on_click=AuthState.logout,
                        background_color="#666",
                        color="#fff",
                        padding="8px 16px",
                        border_radius="5px",
                        _hover={"background_color": "#555"},
                        cursor="pointer",
                    ),
                    spacing="4",
                    justify="center",
                    margin_top="30px",
                ),

                spacing="6",
            ),
            padding="20px",
            background_color="#f5f5f5",
        )
