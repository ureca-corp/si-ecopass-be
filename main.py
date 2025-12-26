"""
Application Entry Point

Run the FastAPI application using Uvicorn
"""

import uvicorn

from src.config import get_settings


def main():
    """Run the FastAPI application"""
    settings = get_settings()

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )


if __name__ == "__main__":
    main()
