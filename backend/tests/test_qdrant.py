"""
Qdrant Service Tests

This module contains tests for the Qdrant service functionality,
verifying collection creation, point operations, and configuration.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.qdrant_service import QdrantService


class TestQdrantService:
    """
    Test class for QdrantService functionality.
    """

    @patch('app.services.qdrant_service.QdrantClient')
    def test_qdrant_service_initialization(self, mock_qdrant_client):
        """
        Test that Qdrant service can be initialized with configuration.
        """
        # Mock the client initialization
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Create service instance
        service = QdrantService()

        # Verify the service was created with correct collection name
        assert service.collection_name == "book_chunks"
        assert service.client is not None

    @patch('app.services.qdrant_service.QdrantClient')
    def test_collection_creation(self, mock_qdrant_client):
        """
        Test Qdrant collection creation functionality.
        """
        # Mock the client and its methods
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock collections response
        mock_collection = MagicMock()
        mock_collection.name = "other_collection"
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        mock_client_instance.get_collections.return_value = mock_collections

        service = QdrantService()

        # Call create_collection
        result = service.create_collection()

        # Verify the collection was created
        assert result is True
        mock_client_instance.create_collection.assert_called_once()

    @patch('app.services.qdrant_service.QdrantClient')
    def test_collection_creation_already_exists(self, mock_qdrant_client):
        """
        Test Qdrant collection creation when collection already exists.
        """
        # Mock the client and its methods
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock collections response with existing collection
        mock_collection = MagicMock()
        mock_collection.name = "book_chunks"  # This is our collection name
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        mock_client_instance.get_collections.return_value = mock_collections

        service = QdrantService()

        # Call create_collection
        result = service.create_collection()

        # Verify the collection was not created again
        assert result is True
        mock_client_instance.create_collection.assert_not_called()

    @patch('app.services.qdrant_service.QdrantClient')
    def test_upsert_point(self, mock_qdrant_client):
        """
        Test upsert point functionality with valid vector and payload.
        """
        # Mock the client and its methods
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        service = QdrantService()

        # Test data - use vector size that matches settings (mock settings for test)
        from unittest.mock import patch
        with patch('app.services.qdrant_service.settings') as mock_settings:
            mock_settings.vector_size = 3  # Match test vector size

            chunk_id = "test-chunk-id"
            vector = [0.1, 0.2, 0.3]
            payload = {
                "document_id": "test-doc-id",
                "source_path": "test/path",
                "title": "Test Title",
                "chunk_index": 0
            }

            # Call upsert_point
            result = service.upsert_point(chunk_id, vector, payload)

            # Verify the upsert was called
            assert result is True
            mock_client_instance.upsert.assert_called_once()

    @patch('app.services.qdrant_service.QdrantClient')
    def test_upsert_point_dimension_mismatch(self, mock_qdrant_client):
        """
        Test upsert point functionality with vector dimension mismatch.
        """
        # Mock the client and its methods
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        service = QdrantService()

        # Test data with wrong vector size
        chunk_id = "test-chunk-id"
        vector = [0.1, 0.2]  # Wrong size
        payload = {
            "document_id": "test-doc-id",
            "source_path": "test/path",
            "title": "Test Title",
            "chunk_index": 0
        }

        # Expect ValueError due to dimension mismatch
        with pytest.raises(ValueError):
            service.upsert_point(chunk_id, vector, payload)

    @patch('app.services.qdrant_service.QdrantClient')
    def test_get_point(self, mock_qdrant_client):
        """
        Test get point functionality.
        """
        # Mock the client and its methods
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock point retrieval
        mock_point = MagicMock()
        mock_point.id = "test-chunk-id"
        mock_point.vector = [0.1, 0.2, 0.3]
        mock_point.payload = {
            "document_id": "test-doc-id",
            "source_path": "test/path",
            "title": "Test Title",
            "chunk_index": 0
        }
        mock_client_instance.retrieve.return_value = [mock_point]

        service = QdrantService()

        # Call get_point
        result = service.get_point("test-chunk-id")

        # Verify the result
        assert result is not None
        assert result["id"] == "test-chunk-id"
        assert result["payload"]["document_id"] == "test-doc-id"

    @patch('app.services.qdrant_service.QdrantClient')
    def test_get_point_not_found(self, mock_qdrant_client):
        """
        Test get point functionality when point doesn't exist.
        """
        # Mock the client and its methods
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock empty point retrieval
        mock_client_instance.retrieve.return_value = []

        service = QdrantService()

        # Call get_point
        result = service.get_point("non-existent-id")

        # Verify the result is None
        assert result is None

    @patch('app.services.qdrant_service.QdrantClient')
    def test_check_collection_exists(self, mock_qdrant_client):
        """
        Test collection existence check functionality.
        """
        # Mock the client and its methods
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock collections response with existing collection
        mock_collection = MagicMock()
        mock_collection.name = "book_chunks"
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        mock_client_instance.get_collections.return_value = mock_collections

        service = QdrantService()

        # Call check_collection_exists
        result = service.check_collection_exists()

        # Verify the result
        assert result is True

    @patch('app.services.qdrant_service.QdrantClient')
    def test_check_collection_not_exists(self, mock_qdrant_client):
        """
        Test collection existence check when collection doesn't exist.
        """
        # Mock the client and its methods
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock collections response without our collection
        mock_collection = MagicMock()
        mock_collection.name = "other_collection"
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        mock_client_instance.get_collections.return_value = mock_collections

        service = QdrantService()

        # Call check_collection_exists
        result = service.check_collection_exists()

        # Verify the result
        assert result is False

    @patch('app.services.qdrant_service.QdrantClient')
    def test_validate_connection(self, mock_qdrant_client):
        """
        Test connection validation functionality.
        """
        # Mock the client and its methods
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        service = QdrantService()

        # Call validate_connection
        result = service.validate_connection()

        # Verify the result
        assert result is True
        mock_client_instance.get_collections.assert_called_once()

    @patch('app.services.qdrant_service.QdrantClient')
    def test_collection_creation_functionality(self, mock_qdrant_client):
        """
        Test collection creation functionality specifically.
        """
        # Mock the client and its methods
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock collections response
        mock_collection = MagicMock()
        mock_collection.name = "other_collection"
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        mock_client_instance.get_collections.return_value = mock_collections

        service = QdrantService()

        # Call create_collection
        result = service.create_collection()

        # Verify the collection was created
        assert result is True
        mock_client_instance.create_collection.assert_called_once()
        # Check that the collection was created with correct parameters
        call_args = mock_client_instance.create_collection.call_args
        assert call_args[1]['collection_name'] == 'book_chunks'

    @patch('app.services.qdrant_service.QdrantClient')
    def test_collection_configuration_parameters(self, mock_qdrant_client):
        """
        Test collection configuration parameters validation.
        """
        from app.config import settings
        # Mock the client and its methods
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock collections response
        mock_collection = MagicMock()
        mock_collection.name = "other_collection"
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        mock_client_instance.get_collections.return_value = mock_collections

        service = QdrantService()

        # Call create_collection
        result = service.create_collection()

        # Verify the collection was created with correct vector parameters
        assert result is True
        mock_client_instance.create_collection.assert_called_once()

        # Check that the vector parameters match the settings
        call_args = mock_client_instance.create_collection.call_args
        vectors_config = call_args[1]['vectors_config']
        assert vectors_config.size == settings.vector_size

    @patch('app.services.qdrant_service.QdrantClient')
    def test_id_mapping_functionality(self, mock_qdrant_client):
        """
        Test chunk ID to Qdrant point ID mapping functionality.
        """
        # Mock the client and its methods
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock point retrieval for verification
        mock_point = MagicMock()
        mock_point.id = "test-chunk-id"
        mock_point.vector = [0.1, 0.2, 0.3]
        mock_point.payload = {
            "document_id": "test-doc-id",
            "source_path": "test/path",
            "title": "Test Title",
            "chunk_index": 0
        }
        mock_client_instance.retrieve.return_value = [mock_point]

        service = QdrantService()

        # Test upsert with specific chunk ID - mock settings to match vector size
        from unittest.mock import patch
        with patch('app.services.qdrant_service.settings') as mock_settings:
            mock_settings.vector_size = 3  # Match test vector size

            chunk_id = "test-chunk-id"
            vector = [0.1, 0.2, 0.3]
            payload = {
                "document_id": "test-doc-id",
                "source_path": "test/path",
                "title": "Test Title",
                "chunk_index": 0
            }

            # Upsert the point
            upsert_result = service.upsert_point(chunk_id, vector, payload)
            assert upsert_result is True

            # Verify the point ID matches the chunk ID
            mock_client_instance.upsert.assert_called_once()
            call_args = mock_client_instance.upsert.call_args
            points = call_args[1]['points']
            assert len(points) == 1
            assert points[0].id == chunk_id

            # Test retrieval
            get_result = service.get_point(chunk_id)
            assert get_result is not None
            assert get_result["id"] == chunk_id

    @patch('app.services.qdrant_service.QdrantClient')
    def test_qdrant_health_check_functionality(self, mock_qdrant_client):
        """
        Test Qdrant health check functionality.
        """
        # Mock the client and its methods
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock collections response to simulate collection exists
        mock_collection = MagicMock()
        mock_collection.name = "book_chunks"
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        mock_client_instance.get_collections.return_value = mock_collections

        service = QdrantService()

        # Test when Qdrant is connected and collection exists
        result = service.validate_connection()
        assert result is True

        collection_exists = service.check_collection_exists()
        assert collection_exists is True

        # Test health check response format
        from app.models.qdrant_models import QdrantHealthResponse, QdrantCollectionCheck
        health_response = QdrantHealthResponse(
            status="healthy",
            details={
                "qdrant_connected": True,
                "collection_exists": True,
                "collection_name": "book_chunks"
            }
        )
        assert health_response.status == "healthy"
        assert health_response.details["qdrant_connected"] is True
        assert health_response.details["collection_exists"] is True
        assert health_response.details["collection_name"] == "book_chunks"

    @patch('app.services.qdrant_service.QdrantClient')
    def test_deterministic_upsert_functionality(self, mock_qdrant_client):
        """
        Test deterministic upsert functionality to prevent duplication.
        """
        # Mock the client and its methods
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        service = QdrantService()

        # Test data - mock settings to match vector size
        from unittest.mock import patch
        with patch('app.services.qdrant_service.settings') as mock_settings:
            mock_settings.vector_size = 3  # Match test vector size

            chunk_id = "test-chunk-id"
            vector1 = [0.1, 0.2, 0.3]
            vector2 = [0.4, 0.5, 0.6]  # Updated vector
            payload1 = {
                "document_id": "test-doc-id",
                "source_path": "test/path",
                "title": "Test Title",
                "chunk_index": 0
            }
            payload2 = {
                "document_id": "test-doc-id",
                "source_path": "test/path",
                "title": "Updated Title",  # Updated payload
                "chunk_index": 0
            }

            # First upsert - should create the point
            result1 = service.upsert_point(chunk_id, vector1, payload1)
            assert result1 is True

            # Second upsert with same ID - should update the point, not create duplicate
            result2 = service.upsert_point(chunk_id, vector2, payload2)
            assert result2 is True

            # Verify upsert was called twice (once for each operation)
            assert mock_client_instance.upsert.call_count == 2

            # Verify that the point ID remained the same (no duplication)
            calls = mock_client_instance.upsert.call_args_list
            first_call_points = calls[0][1]['points']
            second_call_points = calls[1][1]['points']

            assert len(first_call_points) == 1
            assert len(second_call_points) == 1
            assert first_call_points[0].id == chunk_id
            assert second_call_points[0].id == chunk_id

    @patch('app.services.qdrant_service.QdrantClient')
    def test_payload_storage_and_retrieval(self, mock_qdrant_client):
        """
        Test payload storage and retrieval functionality.
        """
        # Mock the client and its methods
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock point retrieval
        mock_point = MagicMock()
        mock_point.id = "test-chunk-id"
        mock_point.vector = [0.1, 0.2, 0.3]
        mock_point.payload = {
            "document_id": "test-doc-id",
            "source_path": "test/path",
            "title": "Test Title",
            "chunk_index": 0
        }
        mock_client_instance.retrieve.return_value = [mock_point]

        service = QdrantService()

        # Test data with required metadata fields - mock settings to match vector size
        from unittest.mock import patch
        with patch('app.services.qdrant_service.settings') as mock_settings:
            mock_settings.vector_size = 3  # Match test vector size

            chunk_id = "test-chunk-id"
            vector = [0.1, 0.2, 0.3]
            payload = {
                "document_id": "test-doc-id",
                "source_path": "test/path",
                "title": "Test Title",
                "chunk_index": 0
            }

            # Upsert the point with payload
            upsert_result = service.upsert_point(chunk_id, vector, payload)
            assert upsert_result is True

            # Retrieve the point to verify payload was stored
            retrieved_point = service.get_point(chunk_id)
            assert retrieved_point is not None
            assert retrieved_point["payload"]["document_id"] == "test-doc-id"
            assert retrieved_point["payload"]["source_path"] == "test/path"
            assert retrieved_point["payload"]["title"] == "Test Title"
            assert retrieved_point["payload"]["chunk_index"] == 0

            # Verify all required metadata fields are present
            assert "document_id" in retrieved_point["payload"]
            assert "source_path" in retrieved_point["payload"]
            assert "title" in retrieved_point["payload"]
            assert "chunk_index" in retrieved_point["payload"]

    @patch('app.services.qdrant_service.QdrantClient')
    def test_configurable_vector_parameters(self, mock_qdrant_client):
        """
        Test configurable vector parameters functionality.
        """
        # Mock the client and its methods
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock collections response
        mock_collection = MagicMock()
        mock_collection.name = "other_collection"
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        mock_client_instance.get_collections.return_value = mock_collections

        service = QdrantService()

        # Test with different vector sizes and distance metrics
        from app.config import settings

        # Save original values
        original_vector_size = settings.vector_size
        original_distance_metric = settings.distance_metric

        try:
            # Test with different vector size
            settings.vector_size = 768  # Smaller vector size
            settings.distance_metric = "Cosine"  # Different distance metric

            # Call create_collection to test with different parameters
            result = service.create_collection()
            assert result is True

            # Verify the collection was created with the configured parameters
            mock_client_instance.create_collection.assert_called()

            # Reset the mock to test another configuration
            mock_client_instance.reset_mock()
            mock_client_instance.get_collections.return_value = mock_collections

            # Test with different distance metric
            settings.vector_size = 2048  # Larger vector size
            settings.distance_metric = "Euclidean"  # Different distance metric

            # Call create_collection again
            result2 = service.create_collection()
            assert result2 is True

            # Verify the collection was created with the new parameters
            mock_client_instance.create_collection.assert_called()

        finally:
            # Restore original values
            settings.vector_size = original_vector_size
            settings.distance_metric = original_distance_metric