#!/usr/bin/env python3
from typing import Callable
from functools import wraps
import requests
import redis
import sys

# Initialize the Redis client
redis_store = redis.Redis(host='localhost', port=6379, db=0)

def data_cacher(method: Callable) -> Callable:
    '''Caches the output of fetched data.'''
    @wraps(method)
    def invoker(url: str) -> str:
        '''The wrapper function for caching the output.'''
        try:
            # Increment the count of how many times this URL has been accessed
            redis_store.incr(f'count:{url}')

            # Check if the result is already cached
            result = redis_store.get(f'result:{url}')
            if result:
                print("Cache hit")
                return result.decode('utf-8')

            # Fetch the result if it's not cached
            result = method(url)

            # Cache the result with an expiration time of 10 seconds
            redis_store.setex(f'result:{url}', 10, result)
            return result
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return "Error fetching the URL"
    
    return invoker

@data_cacher
def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response,
    and tracking the request.'''
    response = requests.get(url)
    return response.text

# Example usage
if __name__ == "__main__":
    url = "http://slowwly.dayoonasanya.com"
    print(get_page(url))
    print(get_page(url))  # This should hit the cache

