#!/usr/bin/env python3
import requests
import redis
from typing import Callable

# Initialize the Redis client
redis_store = redis.Redis()

def data_cacher(method: Callable) -> Callable:
    '''Caches the output of fetched data.'''
    @wraps(method)
    def invoker(url: str) -> str:
        '''The wrapper function for caching the output.'''
        # Increment the count of how many times this URL has been accessed
        redis_store.incr(f'count:{url}')
        
        # Check if the result is already cached
        result = redis_store.get(f'result:{url}')
        if result:
            return result.decode('utf-8')
        
        # Fetch the result if it's not cached
        result = method(url)
        
        # Cache the result with an expiration time of 10 seconds
        redis_store.setex(f'result:{url}', 10, result)
        
        return result
    
    return invoker

@data_cacher
def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response,
    and tracking the request.'''
    response = requests.get(url)
    return response.text

# Example usage
if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk"
    print(get_page(url))

