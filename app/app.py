
import reflex as rx
from app.index_page import index
from app.admin_page import admin



app = rx.App()
app.add_page(index, route="/")
app.add_page(admin, route="/admin")