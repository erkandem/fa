"""
For details see:
https://fastapi.tiangolo.com/tutorial/testing/
"""
from starlette.testclient import TestClient
from app import app

client = TestClient(app)


def test_pulse():
    response = client.get('/pulse')
    assert response.status_code == 200
    assert list(response.json()) == ['date']



