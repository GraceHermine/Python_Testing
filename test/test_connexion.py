import pytest
from server import app, clubs  


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_connexion_email_existant(client):
    """Test connexion avec un email existant"""
    existing_email = clubs[0]['email']
    response = client.post('/showSummary', data={'email': existing_email})
    assert response.status_code == 200
    assert b"Welcome" in response.data or b"welcome" in response.data  


def test_connexion_email_inexistant(client):
    """Test connexion avec un email inexistant -> message flash et redirection vers /connexion"""
    response = client.post('/showSummary', data={'email': 'grace@iit.com'}, follow_redirects=True)
    assert response.status_code == 200  
    # Vérifie le message flash exact (ajuste le texte si tu utilises autre chose)
    assert b"Email inconnu, veuillez ressayer" in response.data


def test_connexion_champ_vide(client):
    """Test connexion avec un champ vide -> message flash et redirection vers /connexion"""
    response = client.post('/showSummary', data={'email': ''}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Veuillez entrer un email." in response.data
