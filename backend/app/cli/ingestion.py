"""
Main CLI command for the document ingestion system.
"""
import typer
import sys
from pathlib import Path
from typing import Optional

# Add the backend directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.config import settings
from app.database.connection import get_db
from app.services.ingestion_service import IngestionService


app = typer.Typer()


@app.command()
def ingest(
    directory: Optional[str] = typer.Option(
        None,
        "--directory",
        "-d",
        help="Directory to scan for documents (defaults to configured source directory)"
    ),
    incremental: bool = typer.Option(
        False,
        "--incremental",
        "-i",
        help="Run incremental ingestion (skip unchanged documents)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging"
    )
):
    """
    Ingest documents from the specified directory into the database and vector store.
    """
    # Validate environment variables
    if not settings.neon_database_url:
        typer.echo("Error: NEON_DATABASE_URL environment variable not set", err=True)
        raise typer.Exit(code=1)

    if not settings.qdrant_url and not (settings.qdrant_host and settings.qdrant_port):
        typer.echo("Error: Qdrant configuration not set (QDRANT_URL or QDRANT_HOST/QDRANT_PORT)", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Starting document ingestion from: {directory or settings.source_directory}")

    # Initialize database connection
    try:
        db_gen = get_db()
        db = next(db_gen)

        # Create ingestion service
        ingestion_service = IngestionService(db)

        # Run ingestion
        if incremental:
            typer.echo("Running incremental ingestion...")
            results = ingestion_service.run_incremental_ingestion(directory)
        else:
            typer.echo("Running full ingestion...")
            results = ingestion_service.run_ingestion_pipeline(directory)

        # Print results
        typer.echo("\n" + "="*50)
        typer.echo("INGESTION RESULTS")
        typer.echo("="*50)
        typer.echo(f"Documents processed: {results['processed_documents']}")
        typer.echo(f"Documents skipped: {results['skipped_documents']}")
        typer.echo(f"Chunks created: {results['created_chunks']}")
        typer.echo(f"Errors encountered: {len(results['errors'])}")

        if results['errors']:
            typer.echo("\nErrors:")
            for error in results['errors']:
                typer.echo(f"  - {error}")

        typer.echo("="*50)

    except Exception as e:
        typer.echo(f"Error during ingestion: {str(e)}", err=True)
        raise typer.Exit(code=1)
    finally:
        # Close database connection
        try:
            next(db_gen)
        except StopIteration:
            pass  # Generator exhausted, connection closed


@app.command()
def validate_config():
    """
    Validate that the required configuration is set.
    """
    typer.echo("Validating configuration...")

    config_issues = []

    if not settings.neon_database_url:
        config_issues.append("NEON_DATABASE_URL not set")

    if not settings.qdrant_url and not (settings.qdrant_host and settings.qdrant_port):
        config_issues.append("Qdrant configuration not set")

    if config_issues:
        for issue in config_issues:
            typer.echo(f"❌ {issue}", err=True)
        raise typer.Exit(code=1)
    else:
        typer.echo("✅ All required configuration is set")


if __name__ == "__main__":
    app()