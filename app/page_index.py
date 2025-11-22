
import reflex as rx
import threading
import os
from demail.gmail import SendEmail
import datetime as dt
from typing import List
import utils.queueing as queueing
from utils.ui_components import song_selector


song_queue_manager = queueing.SongQueueManager()
threading.Thread(target=song_queue_manager.loop_songs, daemon=True).start()


class State(rx.State):
    songs: dict = {}
    song_queue_admin: List[str] = []
    song_queue_requested: List[str] = []
    song_queue_system: List[str] = []
    selected_song: str = ""
    flash_message: str = ""
    song_request_text: str = ""


    @rx.var
    def override(self) -> bool:
        try:
            admin_param = self.router.url.query_parameters.get("admin")
            if not admin_param:
                return False
            return admin_param.lower() == "true"
        except:
            return False


    def on_load(self):
        self.songs = queueing.get_song_list()
        self.update_queues()


    def update_queues(self):
        self.song_queue_requested = song_queue_manager.peek_queues('admin') + song_queue_manager.peek_queues('requested')
        self.song_queue_system = song_queue_manager.peek_queues('system')


    def set_selected_song(self, song: str):
        self.selected_song = song


    def choose_song(self):
        if not self.selected_song:
            self.flash_message = "No song selected. Please choose a song."
            return
        if self.override:
            song_queue_manager.add_song(self.selected_song, "admin")
            self.flash_message = f"Your song '{self.selected_song}' has been added to the queue!"
        elif queueing.check_time():
            song_queue_manager.add_song(self.selected_song, "requested")
            with open('song_requests.txt', 'a') as f:
                timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} - {self.selected_song}\n")
            self.flash_message = f"Your song '{self.selected_song}' has been added to the queue!"
        else:
            self.flash_message = "Current time is outside the allowed range of 5:30p - 8:30p. Song will not be played at this time."
        self.update_queues()
        self.selected_song = ""


    def submit_request(self):
        if self.song_request_text.strip():
            SendEmail(
                to_email_addresses=os.getenv('EMAIL_ADDRESS'),
                subject='LightshowPi Song Request',
                body=self.song_request_text,
                user=os.getenv('EMAIL_UID'),
                password=os.getenv('EMAIL_PWD')
            )
            self.flash_message = f"Your request, {self.song_request_text}, has been submitted. Please check back at a later date."
            self.song_request_text = ""


    def set_song_request_text(self, text: str):
        self.song_request_text = text


@rx.page(route="/")
def index() -> rx.Component:
    return rx.box(
        rx.vstack(
            # Hero Section with gradient background
            rx.box(
                rx.vstack(
                    # Icon header
                    rx.hstack(
                        rx.icon(
                            "sparkles",
                            size=48,
                            color="#10b981",
                            style={
                                "filter": "drop-shadow(0 0 20px rgba(16, 185, 129, 0.6))",
                            },
                        ),
                        rx.icon(
                            "tree-pine",
                            size=64,
                            color="#dc2626",
                            style={
                                "filter": "drop-shadow(0 0 20px rgba(220, 38, 38, 0.6))",
                            },
                        ),
                        rx.icon(
                            "sparkles",
                            size=48,
                            color="#10b981",
                            style={
                                "filter": "drop-shadow(0 0 20px rgba(16, 185, 129, 0.6))",
                            },
                        ),
                        spacing="4",
                        justify="center",
                        margin_bottom="20px",
                    ),
                    # Main heading with gradient text
                    rx.heading(
                        "Linda Ln Christmas Lightshow",
                        font_size="4rem",
                        text_align="center",
                        margin_bottom="15px",
                        font_weight="900",
                        letter_spacing="-0.02em",
                        line_height="1.2",
                        padding="10px 0",
                        style={
                            "background": "linear-gradient(135deg, #dc2626 0%, #b91c1c 50%, #10b981 100%)",
                            "background_clip": "text",
                            "-webkit-background-clip": "text",
                            "-webkit-text-fill-color": "transparent",
                        },
                    ),
                    # Subtitle with time info
                    rx.hstack(
                        rx.icon("clock", size=20, color="#10b981"),
                        rx.text(
                            "Available 5:30 PM - 8:30 PM",
                            color="#f9fafb",
                            font_size="1.1rem",
                            font_weight="600",
                        ),
                        spacing="2",
                        justify="center",
                        padding="12px 24px",
                        background="rgba(255, 255, 255, 0.1)",
                        border_radius="25px",
                        border="2px solid rgba(16, 185, 129, 0.5)",
                        style={
                            "backdrop_filter": "blur(10px)",
                        },
                    ),
                    spacing="4",
                    align="center",
                ),
                padding="60px 20px",
                background="linear-gradient(180deg, #1f2937 0%, #374151 100%)",
                width="100%",
                style={
                    "box_shadow": "0 4px 20px rgba(0, 0, 0, 0.3)",
                },
            ),

            # Song Selection
            song_selector(
                songs_dict=State.songs,
                selected_song=State.selected_song,
                on_song_change=State.set_selected_song,
                on_confirm=State.choose_song,
                flash_message=State.flash_message,
                heading="",
            ),

            # Submit a Request Section
            rx.box(
                rx.vstack(
                    # Section header with icon
                    rx.hstack(
                        rx.icon("mail", size=32, color="#dc2626"),
                        rx.heading(
                            "Request a New Song",
                            font_size="2.5rem",
                            font_weight="800",
                            letter_spacing="-0.02em",
                            line_height="1.3",
                            padding="10px 0",
                            style={
                                "background": "linear-gradient(135deg, #dc2626 0%, #10b981 100%)",
                                "background_clip": "text",
                                "-webkit-background-clip": "text",
                                "-webkit-text-fill-color": "transparent",
                                "display": "inline-block",
                            },
                        ),
                        spacing="3",
                        justify="center",
                        align="center",
                        margin_bottom="15px",
                        padding="10px 0",
                        style={
                            "overflow": "visible",
                        },
                    ),
                    rx.text(
                        "Don't see your favorite song? Request it and we'll add it to our playlist!",
                        color="#6b7280",
                        text_align="center",
                        font_size="1.1rem",
                        margin_bottom="20px",
                    ),
                    # Text area with modern styling
                    rx.text_area(
                        placeholder="Enter song name and your email to be notified when it's added...",
                        value=State.song_request_text,
                        on_change=State.set_song_request_text,
                        width="100%",
                        height="120px",
                        font_size="16px",
                        padding="15px",
                        border_radius="12px",
                        border="2px solid rgba(16, 185, 129, 0.3)",
                        _focus={
                            "border": "2px solid #10b981",
                            "outline": "none",
                            "box_shadow": "0 0 0 3px rgba(16, 185, 129, 0.1)",
                        },
                    ),
                    # Submit button with gradient
                    rx.button(
                        rx.hstack(
                            rx.icon("send", size=20),
                            rx.text("Submit Request", font_size="18px", font_weight="700"),
                            spacing="2",
                            align="center",
                        ),
                        on_click=State.submit_request,
                        width="100%",
                        max_width="250px",
                        height="60px",
                        border_radius="12px",
                        cursor="pointer",
                        style={
                            "background": "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                            "color": "white",
                            "box_shadow": "0 4px 20px rgba(16, 185, 129, 0.4)",
                            "transition": "all 0.3s ease",
                            "_hover": {
                                "background": "linear-gradient(135deg, #059669 0%, #047857 100%)",
                                "transform": "translateY(-2px)",
                                "box_shadow": "0 6px 30px rgba(16, 185, 129, 0.5)",
                            },
                            "_active": {
                                "transform": "translateY(0px)",
                            },
                        },
                    ),
                    spacing="5",
                    align="center",
                ),
                width="100%",
                max_width="900px",
                margin="40px auto",
                padding="40px",
                background="linear-gradient(135deg, #ffffff 0%, #f9fafb 100%)",
                border_radius="20px",
                box_shadow="0 10px 40px rgba(0, 0, 0, 0.1)",
                border="2px solid rgba(220, 38, 38, 0.2)",
            ),

            # Queues Section with Two Columns
            rx.box(
                rx.vstack(
                    # Section header
                    rx.hstack(
                        rx.icon("list-music", size=32, color="#10b981"),
                        rx.heading(
                            "Song Queues",
                            font_size="2.5rem",
                            font_weight="800",
                            letter_spacing="-0.02em",
                            line_height="1.3",
                            padding="10px 0",
                            style={
                                "background": "linear-gradient(135deg, #dc2626 0%, #10b981 100%)",
                                "background_clip": "text",
                                "-webkit-background-clip": "text",
                                "-webkit-text-fill-color": "transparent",
                                "display": "inline-block",
                            },
                        ),
                        spacing="3",
                        justify="center",
                        align="center",
                        margin_bottom="30px",
                        padding="10px 0",
                        style={
                            "overflow": "visible",
                        },
                    ),

                    # Two column layout for queues
                    rx.grid(
                        # User Song Queue
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("users", size=24, color="#dc2626"),
                                    rx.heading(
                                        "Requested Songs",
                                        font_size="1.8rem",
                                        color="#1f2937",
                                        font_weight="700",
                                    ),
                                    spacing="2",
                                    margin_bottom="15px",
                                ),
                                rx.box(
                                    rx.list(
                                        rx.foreach(
                                            State.song_queue_requested,
                                            lambda song: rx.box(
                                                rx.hstack(
                                                    rx.icon("music", size=18, color="#dc2626"),
                                                    rx.text(
                                                        song,
                                                        color="#1f2937",
                                                        font_size="16px",
                                                        font_weight="500",
                                                    ),
                                                    spacing="2",
                                                ),
                                                padding="12px 16px",
                                                margin="8px 0",
                                                background="linear-gradient(135deg, #ffffff 0%, #fef2f2 100%)",
                                                border_radius="10px",
                                                border="1px solid rgba(220, 38, 38, 0.2)",
                                                box_shadow="0 2px 8px rgba(0, 0, 0, 0.05)",
                                                _hover={
                                                    "background": "linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)",
                                                    "transform": "translateX(4px)",
                                                    "transition": "all 0.2s ease",
                                                },
                                            ),
                                        ),
                                    ),
                                    max_height="400px",
                                    overflow_y="auto",
                                    width="100%",
                                ),
                                spacing="4",
                            ),
                            padding="30px",
                            background="linear-gradient(135deg, #ffffff 0%, #f9fafb 100%)",
                            border_radius="16px",
                            box_shadow="0 8px 30px rgba(0, 0, 0, 0.08)",
                            border="2px solid rgba(220, 38, 38, 0.2)",
                        ),

                        # System Song Queue
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("radio", size=24, color="#10b981"),
                                    rx.heading(
                                        "System Playlist",
                                        font_size="1.8rem",
                                        color="#1f2937",
                                        font_weight="700",
                                    ),
                                    spacing="2",
                                    margin_bottom="15px",
                                ),
                                rx.box(
                                    rx.list(
                                        rx.foreach(
                                            State.song_queue_system,
                                            lambda song: rx.box(
                                                rx.hstack(
                                                    rx.icon("music", size=18, color="#10b981"),
                                                    rx.text(
                                                        song,
                                                        color="#1f2937",
                                                        font_size="16px",
                                                        font_weight="500",
                                                    ),
                                                    spacing="2",
                                                ),
                                                padding="12px 16px",
                                                margin="8px 0",
                                                background="linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%)",
                                                border_radius="10px",
                                                border="1px solid rgba(16, 185, 129, 0.2)",
                                                box_shadow="0 2px 8px rgba(0, 0, 0, 0.05)",
                                                _hover={
                                                    "background": "linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)",
                                                    "transform": "translateX(4px)",
                                                    "transition": "all 0.2s ease",
                                                },
                                            ),
                                        ),
                                    ),
                                    max_height="400px",
                                    overflow_y="auto",
                                    width="100%",
                                ),
                                spacing="4",
                            ),
                            padding="30px",
                            background="linear-gradient(135deg, #ffffff 0%, #f9fafb 100%)",
                            border_radius="16px",
                            box_shadow="0 8px 30px rgba(0, 0, 0, 0.08)",
                            border="2px solid rgba(16, 185, 129, 0.2)",
                        ),

                        columns="2",
                        spacing="5",
                        width="100%",
                    ),

                    spacing="5",
                ),
                width="100%",
                max_width="1200px",
                margin="40px auto",
                padding="40px",
            ),

            spacing="0",
        ),
        min_height="100vh",
        background="linear-gradient(180deg, #374151 0%, #4b5563 30%, #6b7280 60%, #9ca3af 100%)",
        on_mount=State.on_load,
    )