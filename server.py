import json
# import datetime
from datetime import datetime
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


# def loadCompetitions():
#     with open('competitions.json') as comps:
#          listOfCompetitions = json.load(comps)['competitions']
#          return listOfCompetitions

def loadCompetitions():
    with open('competitions.json') as comps:
        competitions_data = json.load(comps)['competitions']

        # Filtrer les compétitions futures
        upcoming_competitions = []
        for comp in competitions_data:
            comp_date = datetime.strptime(comp['date'], "%Y-%m-%d %H:%M:%S")
            if comp_date >= datetime.now():
                upcoming_competitions.append(comp)

        return upcoming_competitions
    
reservations = {}   

app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/previews')
def showCompetitions():
    clubs_reservations = []

    for club in clubs:
        club_name = club['name']
        total_reserved = 0

        # Compter le nombre de places réservées par ce club
        for (c_name, comp_name), places in reservations.items():
            if c_name == club_name:
                total_reserved += places

        # Créer une nouvelle entrée mise à jour
        clubs_reservations.append({
            "name": club_name,
            "points": club['points'],
            "total_reserved": total_reserved
        })

    return render_template('dashboard.html', clubs=clubs_reservations, datetime=datetime)


@app.route('/')
def index():
    return redirect(url_for('showCompetitions'))

@app.route('/connexion')
def connexion():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    club = [club for club in clubs if club['email'] == request.form['email']][0]
    return render_template('welcome.html',club=club,competitions=competitions)

# @app.route('/book/<competition>/<club>')
# def book(competition, club):
#     foundCompetition = next((c for c in competitions if c['name'] == competition), None)
#     foundClub = next((c for c in clubs if c['name'] == club), None)

#     if foundClub and foundCompetition:
#         return render_template('booking.html', club=foundClub, competition=foundCompetition)
#     else:
#         flash("Club ou compétition introuvable, merci de réessayer.")
#         return render_template('welcome.html', club=foundClub, competitions=competitions)

@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    foundClub = next((c for c in clubs if c['name'] == club), None)

    if foundClub and foundCompetition:
        already_reserved = reservations.get((foundClub['name'], foundCompetition['name']), 0)
        remaining = 12 - already_reserved  # puisque ta logique est max 12

        return render_template(
            'booking.html',
            club=foundClub,
            competition=foundCompetition,
            remaining=remaining
        )
    else:
        flash("Club ou compétition introuvable, merci de réessayer.")
        return render_template('welcome.html', club=foundClub, competitions=competitions)



@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition_name = request.form.get('competition')
    club_name = request.form.get('club')

    # Récupération club et compétition
    competition = next((c for c in competitions if c['name'] == competition_name), None)
    club = next((c for c in clubs if c['name'] == club_name), None)

    if not competition or not club:
        flash("Erreur : club ou compétition introuvable.")
        return redirect(url_for('index'))

    # Vérification du nombre de places
    try:
        placesRequired = int(request.form.get('places'))
    except (ValueError, TypeError):
        flash("Nombre de places invalide.")
        return redirect(url_for('index'))

    available_places = int(competition['numberOfPlaces'])
    club_points = int(club['points'])

    already_reserved = reservations.get((club_name, competition_name), 0)

    if placesRequired <= 0:
        flash("Vous devez réserver au moins 1 place.")
    elif placesRequired > available_places:
        flash(f"Pas assez de places disponibles (il reste {available_places}).")
    elif placesRequired > club_points:
        flash(f"Pas assez de points. Vous avez {club_points} points.")
    elif already_reserved + placesRequired > 12:
        flash("Vous ne pouvez pas réserver plus de 12 places au totals." f"Vous avez réseveé en tout {already_reserved}")
    else:
        competition['numberOfPlaces'] = available_places - placesRequired
        club['points'] = club_points - placesRequired
        reservations[(club_name, competition_name)] = already_reserved + placesRequired
        flash("Réservation confirmée !")

    return render_template('welcome.html', club=club, competitions=competitions)

# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
