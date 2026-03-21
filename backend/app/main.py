from dotenv import load_dotenv

load_dotenv(".env.local")

from app.core.app_factory import create_app


app = create_app()
