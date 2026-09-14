"""Vercel entrypoint.

Vercel discovers Python functions from ``api/``.  Keeping this tiny wrapper
separate from the application lets local development continue to use
``uvicorn main:app`` while Vercel imports the same ASGI application.
"""
from main import app

__all__ = ["app"]
