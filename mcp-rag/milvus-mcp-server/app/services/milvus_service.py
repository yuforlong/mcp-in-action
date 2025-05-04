import uuid
import json
from typing import Dict, List, Any, Optional, Union
import numpy as np
from pymilvus import connections, utility, Collection, FieldSchema, CollectionSchema, DataType
from loguru import logger

from app.config.settings import (
    MILVUS_HOST, 
    MILVUS_PORT, 
    KNOWLEDGE_COLLECTION, 
    FAQ_COLLECTION,
    TEXT_FIELD, 
    VECTOR_FIELD,
    FAQ_QUESTION_FIELD,
    FAQ_ANSWER_FIELD,
    METADATA_FIELD, 
    VECTOR_DIMENSION
)
from app.models.models import KnowledgeContent, FAQContent
from app.services.embedding_service import EmbeddingService


class MilvusService:
    """Service for interacting with Milvus vector database."""
    
    def __init__(self, embedding_service: EmbeddingService):
        """Initialize the Milvus service.
        
        Args:
            embedding_service: The embedding service to use for creating vectors
        """
        self.embedding_service = embedding_service
        
        # Connect to Milvus
        logger.info(f"Connecting to Milvus at {MILVUS_HOST}:{MILVUS_PORT}")
        connections.connect(
            alias="default", 
            host=MILVUS_HOST, 
            port=MILVUS_PORT
        )
        
        # Initialize collections
        self._init_knowledge_collection()
        self._init_faq_collection()
    
    def _init_knowledge_collection(self):
        """Initialize the knowledge collection."""
        if utility.has_collection(KNOWLEDGE_COLLECTION):
            logger.info(f"Collection {KNOWLEDGE_COLLECTION} already exists")
        else:
            logger.info(f"Creating collection {KNOWLEDGE_COLLECTION}")
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=36),
                FieldSchema(name=TEXT_FIELD, dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name=VECTOR_FIELD, dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIMENSION),
                FieldSchema(name=METADATA_FIELD, dtype=DataType.VARCHAR, max_length=65535)
            ]
            schema = CollectionSchema(fields=fields, description="Knowledge store collection")
            knowledge_collection = Collection(name=KNOWLEDGE_COLLECTION, schema=schema)
            
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
        if utility.has_collection(FAQ_COLLECTION):
            logger.info(f"Collection {FAQ_COLLECTION} already exists")
        else:
            logger.info(f"Creating collection {FAQ_COLLECTION}")
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=36),
                FieldSchema(name=FAQ_QUESTION_FIELD, dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name=FAQ_ANSWER_FIELD, dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name=VECTOR_FIELD, dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIMENSION)
            ]
            schema = CollectionSchema(fields=fields, description="FAQ store collection")
            faq_collection = Collection(name=FAQ_COLLECTION, schema=schema)
            
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
        metadata_json = json.dumps(content.meta_data)
        
        # Insert into collection
        knowledge_collection = Collection(KNOWLEDGE_COLLECTION)
        knowledge_collection.insert([
            [doc_id],
            [content.content],
            [embedding.tolist()],
            [metadata_json]
        ])
        logger.info(f"Stored knowledge document with ID {doc_id}")
    
    def search_knowledge(self, query: str, size: int = 20) -> List[KnowledgeContent]:
        """Search for similar documents in the knowledge collection.
        
        Args:
            query: The query text
            size: The number of results to return
            
        Returns:
            List of knowledge content items
        """
        logger.info(f"Searching knowledge with query: {query}, size: {size}")
        
        # Create embedding for the query
        query_embedding = self.embedding_service.embed(query)
        
        # Search collection
        knowledge_collection = Collection(KNOWLEDGE_COLLECTION)
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
        
        # Convert search results to KnowledgeContent objects
        contents = []
        for hits in results:
            for hit in hits:
                text = hit.entity.get(TEXT_FIELD)
                metadata_str = hit.entity.get(METADATA_FIELD)
                
                try:
                    metadata = json.loads(metadata_str) if metadata_str else {}
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse metadata: {metadata_str}")
                    metadata = {}
                
                contents.append(KnowledgeContent(content=text, meta_data=metadata))
        
        return contents
    
    def store_faq(self, content: FAQContent) -> None:
        """Store an FAQ in the FAQ collection.
        
        Args:
            content: The FAQ content to store
        """
        # Generate a unique ID
        doc_id = str(uuid.uuid4())
        
        # Create embedding for the question
        embedding = self.embedding_service.embed(content.question)
        
        # Insert into collection
        faq_collection = Collection(FAQ_COLLECTION)
        faq_collection.insert([
            [doc_id],
            [content.question],
            [content.answer],
            [embedding.tolist()]
        ])
        logger.info(f"Stored FAQ with ID {doc_id}")
    
    def search_faq(self, query: str, size: int = 20) -> List[FAQContent]:
        """Search for similar FAQs in the FAQ collection.
        
        Args:
            query: The query text
            size: The number of results to return
            
        Returns:
            List of FAQ content items
        """
        logger.info(f"Searching FAQ with query: {query}, size: {size}")
        
        # Create embedding for the query
        query_embedding = self.embedding_service.embed(query)
        
        # Search collection
        faq_collection = Collection(FAQ_COLLECTION)
        search_params = {
            "metric_type": "COSINE",
            "params": {"ef": 64}
        }
        results = faq_collection.search(
            data=[query_embedding.tolist()],
            anns_field=VECTOR_FIELD,
            param=search_params,
            limit=size,
            output_fields=[FAQ_QUESTION_FIELD, FAQ_ANSWER_FIELD]
        )
        
        # Convert search results to FAQContent objects
        contents = []
        for hits in results:
            for hit in hits:
                question = hit.entity.get(FAQ_QUESTION_FIELD)
                answer = hit.entity.get(FAQ_ANSWER_FIELD)
                contents.append(FAQContent(question=question, answer=answer))
        
        return contents
    
    def close(self):
        """Close the connection to Milvus."""
        connections.disconnect("default")
        logger.info("Disconnected from Milvus") 