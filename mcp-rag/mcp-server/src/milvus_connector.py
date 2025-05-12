import uuid
import json
from typing import Dict, List, Any, Optional, Union
import numpy as np
import logging
from pymilvus import connections, utility, Collection, FieldSchema, CollectionSchema, DataType

from embedding import EmbeddingService
from models import KnowledgeContent, FAQContent, SearchResult, FAQSearchResult
from settings import milvus_settings

logger = logging.getLogger(__name__)

# Field name constants
TEXT_FIELD = "text"
VECTOR_FIELD = "vector"
FAQ_QUESTION_FIELD = "question"
FAQ_ANSWER_FIELD = "answer"
METADATA_FIELD = "metadata"


class MilvusConnector:
    """Connector for interacting with Milvus vector database."""
    
    def __init__(self, embedding_service: EmbeddingService):
        """Initialize the Milvus connector.
        
        Args:
            embedding_service: The embedding service to use for creating vectors
        """
        self.embedding_service = embedding_service
        
        # Connect to Milvus
        logger.info(f"Connecting to Milvus at {milvus_settings.HOST}:{milvus_settings.PORT}")
        connections.connect(
            alias="default", 
            host=milvus_settings.HOST, 
            port=milvus_settings.PORT
        )
        
        # Initialize collections
        self._init_knowledge_collection()
        self._init_faq_collection()
    
    def _init_knowledge_collection(self):
        """Initialize the knowledge collection."""
        if utility.has_collection(milvus_settings.KNOWLEDGE_COLLECTION):
            logger.info(f"Collection {milvus_settings.KNOWLEDGE_COLLECTION} already exists")
        else:
            logger.info(f"Creating collection {milvus_settings.KNOWLEDGE_COLLECTION}")
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=36),
                FieldSchema(name=TEXT_FIELD, dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name=VECTOR_FIELD, dtype=DataType.FLOAT_VECTOR, dim=self.embedding_service.dimension),
                FieldSchema(name=METADATA_FIELD, dtype=DataType.VARCHAR, max_length=65535)
            ]
            schema = CollectionSchema(fields=fields, description="Knowledge store collection")
            knowledge_collection = Collection(name=milvus_settings.KNOWLEDGE_COLLECTION, schema=schema)
            
            # Create index for vector field
            index_params = {
                "metric_type": "COSINE",
                "index_type": "HNSW",
                "params": {"M": 8, "efConstruction": 64}
            }
            knowledge_collection.create_index(field_name=VECTOR_FIELD, index_params=index_params)
            knowledge_collection.load()
    
    def _init_faq_collection(self):
        """Initialize the FAQ collection."""
        if utility.has_collection(milvus_settings.FAQ_COLLECTION):
            logger.info(f"Collection {milvus_settings.FAQ_COLLECTION} already exists")
        else:
            logger.info(f"Creating collection {milvus_settings.FAQ_COLLECTION}")
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=36),
                FieldSchema(name=FAQ_QUESTION_FIELD, dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name=FAQ_ANSWER_FIELD, dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name=VECTOR_FIELD, dtype=DataType.FLOAT_VECTOR, dim=self.embedding_service.dimension),
                FieldSchema(name=METADATA_FIELD, dtype=DataType.VARCHAR, max_length=65535)
            ]
            schema = CollectionSchema(fields=fields, description="FAQ store collection")
            faq_collection = Collection(name=milvus_settings.FAQ_COLLECTION, schema=schema)
            
            # Create index for vector field
            index_params = {
                "metric_type": "COSINE",
                "index_type": "HNSW",
                "params": {"M": 8, "efConstruction": 64}
            }
            faq_collection.create_index(field_name=VECTOR_FIELD, index_params=index_params)
            faq_collection.load()
    
    def store_knowledge(self, content: KnowledgeContent) -> None:
        """Store a document in the knowledge collection.
        
        Args:
            content: The knowledge content to store
        """
        # Generate a unique ID
        doc_id = str(uuid.uuid4())
        
        # Create embedding for the content
        embedding = self.embedding_service.embed(content.content)
        
        # Serialize metadata to JSON
        metadata_json = json.dumps(content.metadata)
        
        # Insert into collection
        knowledge_collection = Collection(milvus_settings.KNOWLEDGE_COLLECTION)
        knowledge_collection.insert([
            [doc_id],
            [content.content],
            [embedding.tolist()],
            [metadata_json]
        ])
        logger.info(f"Stored knowledge document with ID {doc_id}")
    
    def search_knowledge(self, query: str, size: int = 5) -> List[SearchResult]:
        """Search for similar documents in the knowledge collection.
        
        Args:
            query: The query text
            size: The number of results to return
            
        Returns:
            List of search result items
        """
        logger.info(f"Searching knowledge with query: {query}, size: {size}")
        
        # Create embedding for the query
        query_embedding = self.embedding_service.embed(query)
        
        # Search collection
        knowledge_collection = Collection(milvus_settings.KNOWLEDGE_COLLECTION)
        search_params = {
            "metric_type": "COSINE",
            "params": {"ef": 64}
        }
        results = knowledge_collection.search(
            data=[query_embedding.tolist()],
            anns_field=VECTOR_FIELD,
            param=search_params,
            limit=size,
            output_fields=[TEXT_FIELD, METADATA_FIELD]
        )
        
        # Convert search results to SearchResult objects
        search_results = []
        for hits in results:
            for hit in hits:
                text = hit.entity.get(TEXT_FIELD)
                metadata_str = hit.entity.get(METADATA_FIELD)
                
                try:
                    metadata = json.loads(metadata_str) if metadata_str else {}
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse metadata: {metadata_str}")
                    metadata = {}
                
                search_results.append(SearchResult(
                    content=text,
                    score=hit.score,
                    metadata=metadata
                ))
        
        return search_results
    
    def store_faq(self, content: FAQContent) -> None:
        """Store an FAQ in the FAQ collection.
        
        Args:
            content: The FAQ content to store
        """
        # Generate a unique ID
        doc_id = str(uuid.uuid4())
        
        # Create embedding for the question
        embedding = self.embedding_service.embed(content.question)
        
        # Serialize metadata to JSON
        metadata_json = json.dumps(content.metadata)
        
        # Insert into collection
        faq_collection = Collection(milvus_settings.FAQ_COLLECTION)
        faq_collection.insert([
            [doc_id],
            [content.question],
            [content.answer],
            [embedding.tolist()],
            [metadata_json]
        ])
        logger.info(f"Stored FAQ with ID {doc_id}")
    
    def search_faq(self, query: str, size: int = 5) -> List[FAQSearchResult]:
        """Search for similar FAQs in the FAQ collection.
        
        Args:
            query: The query text
            size: The number of results to return
            
        Returns:
            List of FAQ search result items
        """
        logger.info(f"Searching FAQ with query: {query}, size: {size}")
        
        # Create embedding for the query
        query_embedding = self.embedding_service.embed(query)
        
        # Search collection
        faq_collection = Collection(milvus_settings.FAQ_COLLECTION)
        search_params = {
            "metric_type": "COSINE",
            "params": {"ef": 64}
        }
        results = faq_collection.search(
            data=[query_embedding.tolist()],
            anns_field=VECTOR_FIELD,
            param=search_params,
            limit=size,
            output_fields=[FAQ_QUESTION_FIELD, FAQ_ANSWER_FIELD, METADATA_FIELD]
        )
        
        # Convert search results to FAQSearchResult objects
        search_results = []
        for hits in results:
            for hit in hits:
                question = hit.entity.get(FAQ_QUESTION_FIELD)
                answer = hit.entity.get(FAQ_ANSWER_FIELD)
                metadata_str = hit.entity.get(METADATA_FIELD)
                
                try:
                    metadata = json.loads(metadata_str) if metadata_str else {}
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse metadata: {metadata_str}")
                    metadata = {}
                
                search_results.append(FAQSearchResult(
                    question=question,
                    answer=answer,
                    score=hit.score,
                    metadata=metadata
                ))
        
        return search_results
    
    def close(self):
        """Close the connection to Milvus."""
        connections.disconnect("default")
        logger.info("Closed connection to Milvus") 