import pytest
from server import app, clubs, competitions, reservations

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret'
    # réinitialiser les reservations à chaque test
    reservations.clear()
    with app.test_client() as client:
        yield client


def test_reservation_max_12_places(client):
    """Un club ne peut pas réserver plus de 12 places dans la même compétition"""
    club = clubs[0]
    comp = competitions[2]

    # D'abord réserver 10 places
    response = client.post('/purchasePlaces', data={
        'competition': comp['name'],
        'club': club['name'],
        'places': 10
    }, follow_redirects=True)

    # Vérifie que le message de confirmation s'affiche bien à l'écran
    html = response.data.decode('utf-8')
    assert "Réservation confirmée" in html or "Reservation confirmee" in html



    # Puis tenter de réserver 5 places supplémentaires → dépasse 12
    response2 = client.post('/purchasePlaces', data={
        'competition': comp['name'],
        'club': club['name'],
        'places': 5
    }, follow_redirects=True)

    # Vérifie que le message d'erreur s'affiche dans la page HTML
    
    html2 = response2.data.decode('utf-8')
    assert (
        "Vous ne pouvez pas réserver plus de 12 places" in html2 or
        "Pas assez de points" in html2
    )



def test_reservation_plus_points(client):
    """Un club ne peut pas réserver plus de places que ses points"""
    club = clubs[1]  # un autre club
    comp = competitions[0]

    # mettons que le club a moins de points que la demande
    club['points'] = 3
    response = client.post('/purchasePlaces', data={
        'competition': comp['name'],
        'club': club['name'],
        'places': 5
    }, follow_redirects=True)
    assert b"Pas assez de points" in response.data


def test_reservation_plus_disponible(client):
    """Un club ne peut pas réserver plus de places que disponibles"""
    club = clubs[2]
    comp = competitions[0]

    # mettons que la compétition n'a que 2 places disponibles
    comp['numberOfPlaces'] = "2"
    response = client.post('/purchasePlaces', data={
        'competition': comp['name'],
        'club': club['name'],
        'places': 5
    }, follow_redirects=True)
    assert b"Pas assez de places disponibles" in response.data


def test_reservation_valide(client):
    """Test qu'une réservation valide s'affiche correctement dans l'interface"""
    club = clubs[3]
    comp = competitions[0]

    # Mettre les points et les places disponibles pour le test
    club['points'] = 10
    comp['numberOfPlaces'] = "10"

    # On effectue la réservation
    response = client.post('/purchasePlaces', data={
        'competition': comp['name'],
        'club': club['name'],
        'places': 5
    }, follow_redirects=True)
    html = response.data.decode()
    # Vérifie que le message de confirmation apparaît dans l'interface
    assert "Réservation confirmée" in html or "Reservation confirmee" in html
    # Vérifie que les nouvelles valeurs sont bien affichées
    assert str(club['points']) in html 
    assert str(int(comp['numberOfPlaces'])) in html  
