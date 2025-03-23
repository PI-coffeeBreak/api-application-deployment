from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from contextlib import asynccontextmanager
from plugin_loader import plugin_loader

from routes import users, activities, activity_types, auth
from routes.ui import page
from dependencies.database import engine, Base
from dependencies.mongodb import db
from routes.ui import main_menu
from schemas.ui.main_menu import MainMenu, MenuOption

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_default_main_menu()
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware( 
    CORSMiddleware, 
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("coffeebreak")

plugin_loader('plugins', app)

class CoffeeBreakLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        logger.debug(f"{request.method} {request.url} - {response.status_code}")
        return response

app.add_middleware(CoffeeBreakLoggerMiddleware)

Base.metadata.create_all(bind=engine)

# Create default main menu if it does not exist
async def create_default_main_menu():
    main_menu_collection = db['main_menu_collection']
    if await main_menu_collection.count_documents({}) == 0:
        default_main_menu = MainMenu(options=[
            MenuOption(icon="home", label="Home", href="/home"),
            MenuOption(icon="profile", label="Profile", href="/profile"),
        ])
        await main_menu_collection.insert_one(default_main_menu.model_dump())

# Include routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(activities.router, prefix="/activities", tags=["Activities"])
app.include_router(activity_types.router, prefix="/activity-types", tags=["Activity Types"])
app.include_router(auth.router, tags=["Auth"])
app.include_router(page.router, prefix="/pages", tags=["Pages"])

# Include UI routers
app.include_router(main_menu.router, prefix="/ui/menu", tags=["Main Menu"])
app.include_router(main_menu.router, prefix="/ui/plugin-config", tags=["Plugin Settings"])

# Run with: uvicorn main:app --reload --log-config logging_config.json
# load env file: --env-file <env_file>
