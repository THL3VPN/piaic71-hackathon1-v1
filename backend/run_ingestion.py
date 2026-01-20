"""
Simple script to run document ingestion without CLI issues.
"""
import sys
import os
from pathlib import Path

# Add the backend directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent))

from app.config import settings
from app.database.connection import get_db
from app.services.ingestion_service import IngestionService

def validate_config():
    """Validate that the required configuration is set."""
    print("Validating configuration...")

    config_issues = []

    if not settings.neon_database_url:
        config_issues.append("NEON_DATABASE_URL not set")

    if not settings.qdrant_url and not (settings.qdrant_host and settings.qdrant_port):
        config_issues.append("Qdrant configuration not set")

    if config_issues:
        for issue in config_issues:
            print(f"❌ {issue}")
        return False
    else:
        print("✅ All required configuration is set")
        return True

def run_ingestion(directory=None):
    """Run the document ingestion process."""
    if not validate_config():
        print("Configuration validation failed. Please check your .env file.")
        return False

    if directory is None:
        directory = settings.source_directory

    print(f"Starting document ingestion from: {directory}")

    # Initialize database connection
    try:
        db_gen = get_db()
        db = next(db_gen)

        # Create ingestion service
        ingestion_service = IngestionService(db)

        # Run ingestion
        print("Running full ingestion...")
        results = ingestion_service.run_ingestion_pipeline(directory)

        # Print results
        print("\n" + "="*50)
        print("INGESTION RESULTS")
        print("="*50)
        print(f"Documents processed: {results['processed_documents']}")
        print(f"Documents skipped: {results['skipped_documents']}")
        print(f"Chunks created: {results['created_chunks']}")
        print(f"Errors encountered: {len(results['errors'])}")

        if results['errors']:
            print("\nErrors:")
            for error in results['errors']:
                print(f"  - {error}")

        print("="*50)

        return True

    except Exception as e:
        print(f"Error during ingestion: {str(e)}")
        return False
    finally:
        # Close database connection
        try:
            next(db_gen)
        except StopIteration:
            pass  # Generator exhausted, connection closed

if __name__ == "__main__":
    # Use the book docs directory as default
    book_docs_dir = "../book/docs"

    if len(sys.argv) > 1:
        book_docs_dir = sys.argv[1]

    success = run_ingestion(book_docs_dir)

    if success:
        print("\n✅ Ingestion completed successfully!")
    else:
        print("\n❌ Ingestion failed!")
        sys.exit(1)