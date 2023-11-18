from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from lamoda.router import lamoda_router
from settings import get_config

setup = get_config()


app = FastAPI(debug=True, openapi_url="/core/openapi.json", docs_url="/core/docs")
app.include_router(router=lamoda_router, prefix=setup.lamoda_prefix)


@app.on_event("startup")
async def startup_event():
    """
    This function is executed when the application starts up. It initializes the Redis cache backend
    and sets up the cache prefix using the provided configuration settings.
    """
    redis = aioredis.from_url(setup.redis_url)
    FastAPICache.init(RedisBackend(redis), prefix=setup.cache_prefix)
