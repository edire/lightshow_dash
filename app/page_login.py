
import reflex as rx
from utils.gauth import AuthState


@rx.page(route="/login")
def login_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            # Logo/Icon area with green glow
            rx.box(
                rx.icon(
                    "chart-line",
                    size=72,
                    style={
                        "color": "#10b981",
                        "filter": "drop-shadow(0 0 40px rgba(16, 185, 129, 0.8))",
                    },
                ),
                margin_bottom="32px",
            ),

            # Main heading with bright silver
            rx.heading(
                "Linda Ln Lightshow",
                size="9",
                text_align="center",
                font_weight="900",
                color="#f8fafc",
                style={
                    "letter_spacing": "-0.02em",
                    "text_shadow": "0 2px 20px rgba(248, 250, 252, 0.5)",
                },
            ),

            # Error message
            rx.cond(
                AuthState.error_message != "",
                rx.callout(
                    AuthState.error_message,
                    icon="triangle_alert",
                    color_scheme="red",
                    role="alert",
                    style={
                        "background": "rgba(239, 68, 68, 0.15)",
                        "backdrop_filter": "blur(10px)",
                        "border": "1px solid rgba(239, 68, 68, 0.4)",
                    },
                ),
            ),

            # Sign in button with green gradient
            rx.button(
                rx.hstack(
                    rx.image(
                        src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg",
                        width="24px",
                        height="24px",
                    ),
                    rx.text("Sign in with Google", font_weight="700", font_size="17px"),
                    spacing="3",
                    align="center",
                ),
                on_click=AuthState.start_oauth_flow,
                size="4",
                style={
                    "background": "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                    "color": "white",
                    "padding": "22px 44px",
                    "border_radius": "16px",
                    "cursor": "pointer",
                    "box_shadow": "0 0 60px rgba(16, 185, 129, 0.5), 0 10px 40px rgba(0, 0, 0, 0.3)",
                    "border": "1px solid rgba(16, 185, 129, 0.3)",
                    "transition": "all 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                    "_hover": {
                        "background": "linear-gradient(135deg, #059669 0%, #047857 100%)",
                        "transform": "translateY(-4px) scale(1.02)",
                        "box_shadow": "0 0 80px rgba(16, 185, 129, 0.7), 0 20px 60px rgba(0, 0, 0, 0.4)",
                    },
                },
            ),

            spacing="8",
            justify="center",
            align="center",
            min_height="100vh",
            max_width="600px",
            margin="0 auto",
            padding="24px",
        ),
        background="linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
        min_height="100vh",
        width="100%",
        position="relative",
        overflow="hidden",
        style={
            "&::before": {
                "content": '""',
                "position": "absolute",
                "top": "0",
                "left": "0",
                "right": "0",
                "bottom": "0",
                "background": "radial-gradient(circle at 30% 20%, rgba(16, 185, 129, 0.15) 0%, transparent 50%), radial-gradient(circle at 70% 80%, rgba(148, 163, 184, 0.1) 0%, transparent 50%)",
                "pointer_events": "none",
            },
            "&::after": {
                "content": '""',
                "position": "absolute",
                "top": "-50%",
                "left": "-50%",
                "width": "200%",
                "height": "200%",
                "background": "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(16, 185, 129, 0.03) 2px, rgba(16, 185, 129, 0.03) 4px)",
                "pointer_events": "none",
            },
        },
    )