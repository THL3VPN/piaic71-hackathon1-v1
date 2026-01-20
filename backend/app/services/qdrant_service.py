"""
Qdrant Service Module

This module provides services for interacting with Qdrant vector database,
including collection management, point operations, and vector storage.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from app.config import settings


logger = logging.getLogger(__name__)


class QdrantService:
    """
    Service class for interacting with Qdrant vector database.
    """

    def __init__(self):
        """
        Initialize Qdrant client with configuration from settings.
        """
        # Use Qdrant URL if provided, otherwise construct from host/port
        if settings.qdrant_url:
            self.client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
        else:
            self.client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                api_key=settings.qdrant_api_key
            )
        self.collection_name = settings.qdrant_collection_name

    def create_collection(self) -> bool:
        """
        Create the Qdrant collection with specified vector parameters.

        Returns:
            bool: True if collection was created or already exists
        """
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            collection_names = [collection.name for collection in collections.collections]

            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return True

            # Determine distance metric from settings
            distance_map = {
                "Cosine": Distance.COSINE,
                "Euclidean": Distance.EUCLID,
                "Dot": Distance.DOT
            }

            distance = distance_map.get(settings.distance_metric, Distance.COSINE)

            # Create collection with specified vector parameters
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.vector_size,
                    distance=distance
                )
            )

            logger.info(f"Created Qdrant collection '{self.collection_name}' with vector_size={settings.vector_size}, distance={settings.distance_metric}")
            return True

        except Exception as e:
            logger.error(f"Error creating Qdrant collection: {str(e)}")
            raise

    def upsert_point(self, chunk_id: str, vector: List[float], payload: Dict[str, Any]) -> bool:
        """
        Upsert a point in Qdrant with the given chunk ID, vector, and payload.

        Args:
            chunk_id: The UUID string of the chunk (used as point ID)
            vector: The embedding vector
            payload: The metadata payload to store

        Returns:
            bool: True if upsert was successful
        """
        try:
            # Validate vector dimensions
            if len(vector) != settings.vector_size:
                raise ValueError(f"Vector dimension mismatch: expected {settings.vector_size}, got {len(vector)}")

            # Validate payload size to avoid Qdrant limits (typically <1MB per point)
            import json
            payload_json = json.dumps(payload)
            payload_size_bytes = len(payload_json.encode('utf-8'))
            max_payload_size = 1024 * 1024  # 1MB in bytes

            if payload_size_bytes > max_payload_size:
                raise ValueError(f"Payload size too large: {payload_size_bytes} bytes, maximum allowed is {max_payload_size} bytes")

            # Prepare point structure
            points = [
                models.PointStruct(
                    id=chunk_id,
                    vector=vector,
                    payload=payload
                )
            ]

            # Upsert the point
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            logger.debug(f"Upserted point with ID '{chunk_id}' to collection '{self.collection_name}'")
            return True

        except Exception as e:
            logger.error(f"Error upserting point with ID '{chunk_id}': {str(e)}")
            raise

    def get_point(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a point from Qdrant by chunk ID.

        Args:
            chunk_id: The UUID string of the chunk

        Returns:
            Optional[Dict]: Point data if found, None otherwise
        """
        try:
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[chunk_id]
            )

            if points and len(points) > 0:
                point = points[0]
                return {
                    "id": point.id,
                    "vector": point.vector,
                    "payload": point.payload
                }
            return None

        except Exception as e:
            logger.error(f"Error retrieving point with ID '{chunk_id}': {str(e)}")
            return None

    def check_collection_exists(self) -> bool:
        """
        Check if the Qdrant collection exists.

        Returns:
            bool: True if collection exists, False otherwise
        """
        try:
            collections = self.client.get_collections()
            collection_names = [collection.name for collection in collections.collections]
            return self.collection_name in collection_names
        except Exception as e:
            logger.error(f"Error checking collection existence: {str(e)}")
            return False

    def validate_connection(self) -> bool:
        """
        Validate connection to Qdrant service.

        Returns:
            bool: True if connection is valid, False otherwise
        """
        try:
            # Try to get collections to verify connection
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Error validating Qdrant connection: {str(e)}")
            return False

    def search_similar(self, query_vector: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the collection.

        Args:
            query_vector: The query vector to search for
            limit: Maximum number of results to return

        Returns:
            List[Dict]: List of similar points with scores
        """
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )

            return [
                {
                    "chunk_id": result.id,
                    "document_id": result.payload.get("document_id"),
                    "source_path": result.payload.get("source_path"),
                    "title": result.payload.get("title"),
                    "chunk_index": result.payload.get("chunk_index"),
                    "score": result.score
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Error performing vector search: {str(e)}")
            return []


# Global instance for use in the application
qdrant_service = QdrantService()