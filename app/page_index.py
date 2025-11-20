
import reflex as rx
import threading
import os
from demail.gmail import SendEmail
import datetime as dt
from typing import List
import utils.queueing as queueing


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
    return rx.container(
        rx.vstack(

            # Heading
            rx.heading(
                "Linda Ln Christmas Lightshow",
                font_size="3rem",
                color="#d32f2f",
                text_align="center",
                margin_bottom="20px",
                font_weight="bold",
                letter_spacing="2px",
            ),
            rx.text(
                "Only available between 5:30p and 8:30p",
                color="#d32f2f",
                text_align="center",
                margin_bottom="10px",
                font_weight="bold",
                letter_spacing="1px",
            ),

            # Song Selection
            rx.box(
                rx.vstack(
                    rx.radio(
                        State.songs.keys(),
                        value=State.selected_song,
                        on_change=State.set_selected_song,
                        direction="column",
                        size="3",
                    ),
                    rx.button(
                        "Confirm",
                        on_click=State.choose_song,
                        width="150px",
                        height="50px",
                        font_size="20px",
                        background_color="#d32f2f",
                        color="#fff",
                        border_radius="5px",
                        font_weight="bold",
                        _hover={"background_color": "#b61f1f"},
                        cursor="pointer",
                    ),
                    spacing="4",
                ),
                width="100%",
                margin="0 auto",
                padding="30px",
                background_color="#fff",
                border_radius="10px",
                box_shadow="0 0 20px rgba(0, 0, 0, 0.1)",
                border="2px solid #d32f2f",
            ),

            # Flash Message
            rx.cond(
                State.flash_message != "",
                rx.box(
                    rx.text(
                        State.flash_message,
                        color="#cc201a",
                        text_align="center",
                        font_size="18px",
                        font_weight="bold",
                    ),
                    max_width="600px",
                    margin="20px auto",
                    padding="10px",
                ),
            ),

            # Submit a Request
            rx.box(
                rx.vstack(
                    rx.heading(
                        "Submit a Request",
                        font_size="2rem",
                        color="#333",
                        margin_bottom="10px",
                    ),
                    rx.text_area(
                        placeholder="Submit a song and leave your email to be notified when added.",
                        value=State.song_request_text,
                        on_change=State.set_song_request_text,
                        width="100%",
                    ),
                    rx.button(
                        "Submit",
                        on_click=State.submit_request,
                        width="150px",
                        height="50px",
                        font_size="20px",
                        background_color="#d32f2f",
                        color="#fff",
                        border_radius="5px",
                        font_weight="bold",
                        _hover={"background_color": "#b61f1f"},
                        cursor="pointer",
                    ),
                    spacing="4",
                ),
                width="100%",
                # max_width="600px",
                margin="20px auto",
                padding="30px",
                background_color="#fff",
                border_radius="10px",
                box_shadow="0 0 20px rgba(0, 0, 0, 0.1)",
                border="2px solid #d32f2f",
            ),

            # User Song Queue
            rx.box(
                rx.vstack(
                    rx.heading(
                        "User Song Queue",
                        font_size="2rem",
                        color="#d32f2f",
                        margin_bottom="20px",
                        text_align="center",
                    ),
                    rx.list(
                        rx.foreach(
                            State.song_queue_requested,
                            lambda song: rx.list_item(
                                song,
                                background_color="#fff",
                                margin="10px 0",
                                padding="15px",
                                border_radius="8px",
                                box_shadow="0 2px 4px rgba(0, 0, 0, 0.1)",
                            ),
                        ),
                    ),
                    spacing="4",
                ),
                width="100%",
                margin="20px auto",
                padding="30px",
                background_color="#e6e6e6",
                border_radius="10px",
                box_shadow="0 0 20px rgba(0, 0, 0, 0.1)",
                border="2px solid #d32f2f",
            ),

            # System Song Queue
            rx.box(
                rx.vstack(
                    rx.heading(
                        "System Song Queue",
                        font_size="2rem",
                        color="#d32f2f",
                        margin_bottom="20px",
                        text_align="center",
                    ),
                    rx.list(
                        rx.foreach(
                            State.song_queue_system,
                            lambda song: rx.list_item(
                                song,
                                background_color="#fff",
                                margin="10px 0",
                                padding="15px",
                                border_radius="8px",
                                box_shadow="0 2px 4px rgba(0, 0, 0, 0.1)",
                            ),
                        ),
                    ),
                    spacing="4",
                ),
                width="100%",
                margin="20px auto",
                padding="30px",
                background_color="#e6e6e6",
                border_radius="10px",
                box_shadow="0 0 20px rgba(0, 0, 0, 0.1)",
                border="2px solid #d32f2f",
            ),
            spacing="6",
        ),
        padding="20px",
        background_color="#59c759",
        on_mount=State.on_load,
    )