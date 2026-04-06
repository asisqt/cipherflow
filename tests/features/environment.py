from fastapi.testclient import TestClient
from src.main import app

def before_scenario(context, scenario):
    context.client = TestClient(app)
    context.token = None
    context.response = None
    context.payload = {}
    context.encrypted = False
