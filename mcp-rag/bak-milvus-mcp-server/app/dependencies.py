"""
依赖注入模块 - Dependencies Module
本模块提供了系统各服务组件的依赖注入功能，实现了服务的单例模式和依赖管理。
主要包含了向量嵌入服务(EmbeddingService)和Milvus向量数据库服务(MilvusService)的获取方法，
确保在整个应用程序中只有一个服务实例，从而提高资源利用率和性能。

This module provides dependency injection for service components in the system,
implementing singleton pattern and dependency management.
"""

from functools import lru_cache
from typing import Generator

from app.services.embedding_service import EmbeddingService
from app.services.milvus_service import MilvusService


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    """获取向量嵌入服务的单例实例。
    
    使用lru_cache装饰器确保只创建一个EmbeddingService实例，实现单例模式。
    
    Returns:
        EmbeddingService: 向量嵌入服务实例
    """
    return EmbeddingService()


@lru_cache(maxsize=1)
def get_milvus_service() -> MilvusService:
    """获取Milvus向量数据库服务的单例实例。
    
    使用lru_cache装饰器确保只创建一个MilvusService实例，实现单例模式。
    该服务依赖于EmbeddingService，通过get_embedding_service()获取依赖。
    
    Returns:
        MilvusService: Milvus向量数据库服务实例
    """
    embedding_service = get_embedding_service()
    return MilvusService(embedding_service)


def get_milvus_service_dependency() -> MilvusService:
    """Milvus服务的依赖获取函数。
    
    返回MilvusService实例，而不是使用生成器函数。
    这样可以避免在初始化过程中出现的问题，确保服务实例在使用前完全初始化。
    
    Returns:
        MilvusService: Milvus向量数据库服务实例
    """
    return get_milvus_service() 