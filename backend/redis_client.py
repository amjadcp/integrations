import os
import redis.asyncio as redis
from kombu.utils.url import safequote

from config.settings import get_settings

settings = get_settings()
REDIS_URI = settings.REDIS_URI
redis_client = redis.from_url(REDIS_URI)

async def add_key_value_redis(key, value, expire=None):
    await redis_client.set(key, value)
    if expire:
        await redis_client.expire(key, expire)

async def get_value_redis(key):
    return await redis_client.get(key)

async def delete_key_redis(key):
    await redis_client.delete(key)
