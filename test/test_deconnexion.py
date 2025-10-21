import pytest
from server import app  


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_logout(client):
    """Test que la déconnexion redirige vers la page d'accueil"""
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    # Vérifie que la page d'accueil affiche bien le titre attendu
    assert b"Liste des clubs" in response.data
