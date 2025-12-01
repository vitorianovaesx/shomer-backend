"""Main CLI entry point."""

import asyncio
import sys
from pathlib import Path

import uvicorn

from internal.config import load_config


def serve():
    """Run the API server."""
    config = load_config()
    uvicorn.run(
        "api.main:app",
        host=config.api.host,
        port=config.api.port,
        reload=False,
    )


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m cmd.shomer [serve|ingest|admin]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "serve":
        serve()
    elif command == "ingest":
        if len(sys.argv) < 3:
            print("Usage: python -m cmd.shomer ingest <url>")
            sys.exit(1)
        url = sys.argv[2]
        asyncio.run(ingest_url(url))
    elif command == "admin":
        print("Admin CLI not yet implemented")
        sys.exit(1)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


async def ingest_url(url: str):
    """Ingest a URL via CLI."""
    from internal.config import load_config
    from internal.pipeline import IngestionPipeline

    config = load_config()
    pipeline = IngestionPipeline(config)

    try:
        case_id = await pipeline.ingest(url)
        print(f"Case created: {case_id}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await pipeline.close()


if __name__ == "__main__":
    main()

