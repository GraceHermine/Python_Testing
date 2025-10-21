import pytest
from server import app


def test():
    app.testing = True
    client = app.test_client()

    response = client.get('/')
    assert response.status_code == 302 or response.status_code == 200
