import pytest
from datetime import datetime
from server import app, competitions

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_showSummary_ne_affiche_pas_anciennes_competitions(client):
    """Vérifie que les compétitions passées ne s'affichent pas dans showSummary"""
    
    #  On suppose qu’un club existe dans ton fichier clubs.json
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})  

    html = response.data.decode()

    #  Récupère la date actuelle
    now = datetime.now()

    #  Vérifie que chaque compétition affichée est dans le futur
    competitions_affichees = [c for c in competitions]
    erreurs = []

    for comp in competitions_affichees:
        date_comp = datetime.strptime(comp['date'], "%Y-%m-%d %H:%M:%S")
        if date_comp < now and comp['name'] in html:
            erreurs.append(comp['name'])

    #  Si on trouve une ancienne compétition dans la page → erreur
    assert not erreurs, f"Les compétitions passées suivantes apparaissent encore : {erreurs}"
