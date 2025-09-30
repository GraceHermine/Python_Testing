import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/showSummary',methods=['POST'])
def showSummary():
    club = [club for club in clubs if club['email'] == request.form['email']][0]
    return render_template('welcome.html',club=club,competitions=competitions)

@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    foundClub = next((c for c in clubs if c['name'] == club), None)

    if foundClub and foundCompetition:
        return render_template('booking.html', club=foundClub, competition=foundCompetition)
    else:
        flash("❌ Club ou compétition introuvable, merci de réessayer.")
        return render_template('welcome.html', club=foundClub, competitions=competitions)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition_name = request.form.get('competition')
    club_name = request.form.get('club')

    # Récupération club et compétition
    competition = next((c for c in competitions if c['name'] == competition_name), None)
    club = next((c for c in clubs if c['name'] == club_name), None)

    if not competition or not club:
        flash("❌ Erreur : club ou compétition introuvable.")
        return redirect(url_for('index'))

    # Vérification du nombre de places
    try:
        placesRequired = int(request.form.get('places'))
    except (ValueError, TypeError):
        flash("⚠️ Nombre de places invalide.")
        return redirect(url_for('index'))

    available_places = int(competition['numberOfPlaces'])
    club_points = int(club['points'])

    if placesRequired <= 0:
        flash("⚠️ Vous devez réserver au moins 1 place.")
    elif placesRequired > available_places:
        flash(f"⚠️ Pas assez de places disponibles (il reste {available_places}).")
    elif placesRequired > club_points:
        flash(f"⚠️ Pas assez de points. Vous avez {club_points} points.")
    else:
        competition['numberOfPlaces'] = available_places - placesRequired
        club['points'] = club_points - placesRequired
        flash("Réservation confirmée !")

    return render_template('welcome.html', club=club, competitions=competitions)

# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
