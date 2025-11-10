import reflex as rx

config = rx.Config(
    app_name="app",
    api_url="http://localhost:8000",
    backend_port=8000,
    frontend_port=3000,
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
)
