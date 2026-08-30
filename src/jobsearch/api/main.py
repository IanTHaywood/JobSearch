from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jobsearch.api.routes_cron import router as cron_router
from jobsearch.api.routes_ingest import router as ingest_router
from jobsearch.api.routes_listings import router as listings_router
from jobsearch.api.scheduler import get_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_scheduler()  # starts the background scheduler + loads persisted jobs
    yield


app = FastAPI(title="JobSearch Control API", lifespan=lifespan)

# Vite's default dev server port.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(listings_router)
app.include_router(ingest_router)
app.include_router(cron_router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
