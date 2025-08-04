from django.core.cache import cache
from django.conf import settings
import hashlib
from typing import List, Optional, Union
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class CacheKeys:
    RECIPE_DETAIL = 'recipe:detail:{recipe_id}'
    RECIPE_LIST = 'recipe:list:{filters_hash}'
    RECIPE_POPULAR = 'recipe:popular'
    RECIPE_FODMAP = 'recipe:fodmap'
    USER_PROFILE = 'user:profile:{user_id}'
    USER_FAVORITES = 'user:favorites:{user_id}'
    USER_STATISTICS = 'user:stats:{user_id}'
    INGREDIENT_AUTOCOMPLETE = 'ingredient:autocomplete:{term}'
    
    TTL_SHORT = 60 * 5
    TTL_MEDIUM = 60 * 10
    TTL_LONG = 60 * 60 * 24
    
    @classmethod
    def get_recipe_detail(cls, recipe_id: str | int) -> str:
        return cls.RECIPE_DETAIL.format(recipe_id=recipe_id)
    
    @classmethod
    def get_recipe_list(cls, **filters) -> str:
        filters_str = ':'.join('f{k}={v}' for k,v in sorted(filters.items()))
        filters_hash = hashlib.md5(filters_str.encode()).hexdigest()[:8]
        return cls.RECIPE_LIST.format(filters_hash=filters_hash)
    
    @classmethod
    def get_user_profile(cls, user_id: str | int) -> str:
        return cls.USER_PROFILE.format(user_id=user_id)
    
    @classmethod
    def get_user_favorites(cls, user_id: str | int) -> str:
        return cls.USER_FAVORITES.format(user_id=user_id)
    
class CacheTagManager:
    """Invalidate cache based on tags"""
    
    @staticmethod
    def tag_key(tag:str) -> str:
        """Generate key for storing cached keys"""
        return f'tag:{tag}:keys'
    
    @classmethod
    def add_tags(cls, cache_key:str, tags: List[str]):
        """Associate cache key with tags for bulk invalidation"""
        for tag in tags:
            tag_key = cls.tag_key(tag)
            tagged_keys = cache.get(tag_key, set())
            tagged_keys.add(cache_key)
            cache.set(tag_key, tagged_keys, CacheKeys.TTL_LONG)
            
    @classmethod
    def invalidate_tag(cls, tag: str):
        """Invalidate all cache keys associated with a tag"""
        tag_key = cls.tag_key(tag)
        tagged_keys = cache.get(tag_key, set())
        
        for key in tagged_keys:
            cache.delete(key)
            
        cache.delete(tag_key)
        logger.info(f'Invalidated {len(tagged_keys)} cache keys for tag {tag}.')

    @classmethod
    def invalidate_tags(cls, tags: List[str]):
        """Invalidate multiple tags"""
        for tag in tags:
            cls.invalidate_tag(tag)
            
def cache_with_tags(key_func, tags_func, ttl=CacheKeys.TTL_MEDIUM):
    """Decorator for caching with tag-based invalidation

    Args:
        key_func: lambda self, recipe_id: CacheKeys.get_recipe_detail(recipe_id)
        tags_func: lambda self, recipe_id: [f'recipe:{recipe_id}', 'recipe:all'] 
        ttl: Defaults to CacheKeys.TTL_MEDIUM.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = key_func(*args, **kwargs)
            
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            tags = tags_func(*args, **kwargs)
            CacheTagManager.add_tags(cache_key, tags)
            
            return result
        return wrapper
    return decorator
    
def invalidate_recipe_cache(recipe_id: str | int):
    """Invalidate all caches related to recipe using tags"""
    CacheTagManager.invalidate_tags([
        f'recipe:{recipe_id}',
        'recipe:all',
        'recipe:popular'
    ])
    
def invalidate_user_caches(user_id: str | int):
    """Invalidate all caches related to a user using tags"""
    CacheTagManager.invalidate_tags([
        f'user:{user_id}',
        'user:stats'
    ])