import asyncio

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from lamoda.router import lamoda_router
from twitch.router import twitch_router
from settings import get_config
from broker import KafkaWorker

setup = get_config()

app = FastAPI(debug=True, openapi_url="/core/openapi.json", docs_url="/core/docs")
app.include_router(router=lamoda_router, prefix=setup.lamoda_prefix)
app.include_router(router=twitch_router, prefix=setup.twitch_prefix)


async def startup_event_cache():
    """
    Initialize the Redis cache backend and set up the cache prefix.

    This function is executed when the application starts up.
    """
    redis = aioredis.from_url(setup.redis_url)
    FastAPICache.init(RedisBackend(redis), prefix=setup.cache_prefix)


async def startup_tasks():
    """
    Execute startup tasks.

    This function creates a list of tasks to be executed on application startup,
    including consuming messages from Kafka and initializing the cache backend.
    """
    tasks = [KafkaWorker().start_consuming(), startup_event_cache()]
    await asyncio.gather(*tasks)


@app.on_event("startup")
async def startup_event():
    """
    Application startup event.

    This function creates a new asyncio task to execute the startup tasks.
    """
    asyncio.create_task(startup_tasks())
