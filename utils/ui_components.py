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
    Reusable song selector component with professional styling.

    Args:
        songs_dict: Dictionary of available songs
        selected_song: Currently selected song
        on_song_change: Callback when song selection changes
        on_confirm: Callback when confirm button is clicked
        flash_message: Optional flash message to display
        heading: Optional heading text
    """
    return rx.vstack(
        # Optional heading with icon
        rx.cond(
            heading != "",
            rx.hstack(
                rx.icon("music", size=32, color="#10b981"),
                rx.heading(
                    heading,
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
                margin_bottom="25px",
                padding="10px 0",
                style={
                    "overflow": "visible",
                },
            ),
        ),

        # Song Selection Box with modern styling
        rx.box(
            rx.vstack(
                # Radio buttons with better spacing
                rx.box(
                    rx.radio(
                        songs_dict.keys(),
                        value=selected_song,
                        on_change=on_song_change,
                        direction="column",
                        size="3",
                        color_scheme="green",
                    ),
                    max_height="400px",
                    overflow_y="auto",
                    width="100%",
                    padding="10px",
                ),
                # Confirm button with gradient
                rx.button(
                    rx.hstack(
                        rx.icon("play", size=20),
                        rx.text("Play Song", font_size="18px", font_weight="700"),
                        spacing="2",
                        align="center",
                    ),
                    on_click=on_confirm,
                    width="100%",
                    max_width="250px",
                    height="60px",
                    border_radius="12px",
                    cursor="pointer",
                    margin_top="20px",
                    style={
                        "background": "linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)",
                        "color": "white",
                        "box_shadow": "0 4px 20px rgba(220, 38, 38, 0.4)",
                        "transition": "all 0.3s ease",
                        "_hover": {
                            "background": "linear-gradient(135deg, #b91c1c 0%, #991b1b 100%)",
                            "transform": "translateY(-2px)",
                            "box_shadow": "0 6px 30px rgba(220, 38, 38, 0.5)",
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
            margin="0 auto",
            padding="40px",
            background="linear-gradient(135deg, #ffffff 0%, #f9fafb 100%)",
            border_radius="20px",
            box_shadow="0 10px 40px rgba(0, 0, 0, 0.1)",
            border="2px solid rgba(16, 185, 129, 0.2)",
        ),

        # Flash Message with modern styling
        rx.cond(
            flash_message != "",
            rx.box(
                rx.hstack(
                    rx.icon("check-circle", size=24, color="#10b981"),
                    rx.text(
                        flash_message,
                        color="#065f46",
                        font_size="16px",
                        font_weight="600",
                    ),
                    spacing="3",
                    align="center",
                    justify="center",
                ),
                max_width="700px",
                margin="20px auto",
                padding="16px 24px",
                background="linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)",
                border_radius="12px",
                border="2px solid #10b981",
                box_shadow="0 4px 15px rgba(16, 185, 129, 0.2)",
            ),
        ),

        spacing="5",
        width="100%",
        max_width="900px",
        margin="0 auto",
        padding="40px 20px",
    )
