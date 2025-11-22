import reflex as rx


def song_selector(
    songs_dict,
    selected_song,
    on_song_change,
    on_confirm,
    flash_message: str = "",
    heading: str = "Choose Your Song",
) -> rx.Component:
    """
    Reusable song selector component.

    Args:
        songs_dict: Dictionary of available songs
        selected_song: Currently selected song
        on_song_change: Callback when song selection changes
        on_confirm: Callback when confirm button is clicked
        flash_message: Optional flash message to display
        heading: Optional heading text
    """
    return rx.vstack(
        # Optional heading
        rx.cond(
            heading != "",
            rx.heading(
                heading,
                font_size="2rem",
                color="#333",
                margin_bottom="15px",
            ),
        ),

        # Song Selection Box
        rx.box(
            rx.vstack(
                rx.radio(
                    songs_dict.keys(),
                    value=selected_song,
                    on_change=on_song_change,
                    direction="column",
                    size="3",
                ),
                rx.button(
                    "Confirm",
                    on_click=on_confirm,
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
            flash_message != "",
            rx.box(
                rx.text(
                    flash_message,
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

        spacing="4",
        width="100%",
    )
