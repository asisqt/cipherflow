"""
Behave Environment
===================
Setup and teardown for BDD test scenarios.
Initializes the FastAPI TestClient before each scenario.
"""

from fastapi.testclient import TestClient
from src.main import app


def before_scenario(context, scenario):
    """Create a fresh test client for each scenario."""
    context.client = TestClient(app)
    context.api = "/api/v1"
    context.token = None
    context.response = None
