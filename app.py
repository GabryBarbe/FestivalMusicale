import os
from flask import Flask, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import User
import tickets_dao
import utenti_dao, ruoli_dao, performances_dao, palchi_dao, immagini_dao

app = Flask(__name__)
app.config["SECRET_KEY"] = "SunRiftSecretKey!"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # redirect alla pagina di login quando è richiesto il login

# Numero di ticket disponibili per ogni giorno
ticket_venerdi = 200 - tickets_dao.get_ticket_number_venerdi()
ticket_sabato = 200 - tickets_dao.get_ticket_number_sabato()
ticket_domenica = 200 - tickets_dao.get_ticket_number_domenica()

@login_manager.user_loader
def load_user(user_id):
    user_data = utenti_dao.get_user_by_id(user_id)
    if user_data:
        return User(
            id=user_data['id'],
            email=user_data['email'],
            password=user_data['password'],
            nome=user_data['nome'],
            cognome=user_data['cognome'],
            ruolo=user_data['ruolo']
        )
    return None


# Filtro custom per percentuale progress bar biglietti
@app.template_filter('progress_percent')
def progress_percent_filter(n):
    return (int) ((n / 200) * 100)


# FUNZIONI DI ROUTING

@app.route('/')
def homepage():
    perf_list = performances_dao.get_performances_ordered()
    perf_list = [p for p in perf_list if p['Pubblicata'] == 1]  # Filtra solo le performance pubblicate
    for performance in perf_list:
        # Ottengo la prima immagine associata alla performance
        immagini = immagini_dao.get_images_by_performance_id(performance['ID'])
        performance['Immagine'] = immagini[0] if immagini else None
        # Ottengo il nome del palco associato alla performance
        performance['Palco'] = palchi_dao.get_stage_name_by_id(performance['Palco'])

    # prendi solo il nome del palco (numero 1 nella tupla)
    palchi = [p[1] for p in palchi_dao.get_all_stages()]
    generi = performances_dao.get_all_genres_of_public_performances()

    if current_user.is_authenticated:
        return render_template('homepage.html', p_nome_utente=current_user.nome, 
                               p_cognome_utente=current_user.cognome, 
                               p_performances_list=perf_list, p_palchi=palchi, 
                               p_generi=generi)

    return render_template('homepage.html', p_performances_list=perf_list,
                           p_palchi=palchi, p_generi=generi)

@app.route('/signup')
def signup():
    ruoli = ruoli_dao.get_all_roles()
    return render_template('signup.html', p_ruoli=ruoli)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('homepage'))

@app.route('/profile')
@login_required
def profile():
    role = ruoli_dao.get_role_by_id(current_user.ruolo)
    stat_venerdi = tickets_dao.get_ticket_number_venerdi()
    stat_sabato = tickets_dao.get_ticket_number_sabato()
    stat_domenica = tickets_dao.get_ticket_number_domenica()
    if (current_user.ruolo == 2):
        palchi = palchi_dao.get_all_stages()
        performances = performances_dao.get_all_public_performances()
        for performance in performances:
            immagini = immagini_dao.get_images_by_performance_id(performance['ID'])
            performance['Immagine'] = immagini[0] if immagini else None
        draft = performances_dao.get_draft_performances_by_organizer(current_user.id)
        for performance in draft:
            immagini = immagini_dao.get_images_by_performance_id(performance['ID'])
            performance['Immagine'] = immagini[0] if immagini else None
        return render_template('profile.html', p_ruolo=role[0], p_palchi=palchi, p_performances_list=performances, p_performances_draft_list=draft,
            stat_venerdi=stat_venerdi, stat_sabato=stat_sabato, stat_domenica=stat_domenica)
    else:
        ticket_id = utenti_dao.get_ticket_by_user_id(current_user.id)
        return render_template('profile.html', p_ruolo=role[0], p_ticket=tickets_dao.get_ticket_by_id(ticket_id) if ticket_id else None)

@app.route('/infopage')
def infopage():
    return render_template('infopage.html')

@app.route('/performance/<int:performance_id>')
def performance(performance_id):
    perf = performances_dao.get_performance_by_id(performance_id)
    # Converto il campo "GiornoInizio" con la maiuscola
    perf['GiornoInizio'] = perf['GiornoInizio'].capitalize()
    # Converto il campo "Palco" con il suo nome completo
    perf['Palco'] = palchi_dao.get_stage_name_by_id(perf['Palco'])

    immagini = immagini_dao.get_images_by_performance_id(performance_id)
    palchi = palchi_dao.get_all_stages()

    # Ammette modifica solo se la performance non è pubblicata e l'utente è l'organizzatore
    if (perf['Pubblicata'] == 0 and perf['OrganizzatoreID'] == current_user.id):
        return render_template('performance.html', p_immagini=immagini, p_performance=perf, 
                               p_edit=True, p_palchi=palchi)

    return render_template('performance.html', p_immagini=immagini, p_performance=perf)

@app.route('/tickets')
def tickets():
    global ticket_venerdi, ticket_sabato, ticket_domenica
    disponibili = [ticket_venerdi, ticket_sabato, ticket_domenica]
    return render_template('tickets.html', p_disponibilita=disponibili)

@app.route('/buy-ticket')
@login_required
def buy_ticket_page():
    return render_template('buy_ticket.html', p_utente=current_user)

@app.route('/come-raggiungerci')
def come_raggiungerci():
    return render_template('raggiungici.html')

@app.route('/contattaci')
def contattaci():
    return render_template('contacts.html')

# FUNZIONI DI REGISTRAZIONE, AUTENTICAZIONE E LOGOUT

@app.route('/signup-create-account', methods=['POST'])
def signup_create_account():
    dati_form = {
        'nome': request.form.get('nome'),
        'cognome': request.form.get('cognome'),
        'email': request.form.get('email'),
        'password': request.form.get('password'),
        'ruolo': request.form.get('ruolo')
    }

    # Validazione dei campi nome, cognome, email e password
    if not dati_form['nome'] or not dati_form['cognome'] or not dati_form['email'] or not dati_form['password']:
        ruoli = ruoli_dao.get_all_roles()
        return render_template('signup.html', alert_message="Tutti i campi sono obbligatori!", p_ruoli=ruoli)
    if "@" not in dati_form['email'] or len(dati_form['password']) < 8:
        ruoli = ruoli_dao.get_all_roles()
        return render_template('signup.html', alert_message="Email o Password non validi!", p_ruoli=ruoli)

    # Controlla se l'email è già registrata
    if dati_form['email'] in utenti_dao.get_emails_of_registered_users():
        ruoli = ruoli_dao.get_all_roles()
        return render_template('signup.html', alert_message="Email già registrata!", p_ruoli=ruoli)

    dati_form['password'] = generate_password_hash(dati_form['password'], method="pbkdf2:sha256")

    utenti_dao.insert_user(dati_form)

    user_db = utenti_dao.get_user_by_email(dati_form['email'])

    user = User(
        id=user_db['ID'],
        email=user_db['Email'],
        password=user_db['Password'],
        nome=user_db['Nome'],
        cognome=user_db['Cognome'],
        ruolo=user_db['Ruolo']
    )

    login_user(user)  # Effettua il login dell'utente appena registrato

    return redirect(url_for('homepage'))

@app.route('/login-autenticate', methods=['POST'])
def login_authenticate():
    email_form = request.form.get('email')
    password_form = request.form.get('password')
    remember_me = (request.form.get('remember') == 'on')

    # Validazione
    if not email_form or not password_form:
        return render_template('login.html', alert_message="Tutti i campi sono obbligatori!")
    if "@" not in email_form or len(password_form) < 8:
        return render_template('login.html', alert_message="Email o Password non validi!")

    # Controllo email e password
    if email_form not in utenti_dao.get_emails_of_registered_users():
        return render_template('login.html', alert_message="Email o Password non validi!")

    utente_db = utenti_dao.get_user_by_email(email_form)
    if not utente_db:
        return render_template('login.html', alert_message="Utente non trovato!")

    # Verifica la password hashata
    if not check_password_hash(utente_db['Password'], password_form):
        return render_template('login.html', alert_message="Email o Password non validi!")

    utente = User(
        id=utente_db['ID'],
        email=utente_db['Email'],
        password=utente_db['Password'],
        nome=utente_db['Nome'],
        cognome=utente_db['Cognome'],
        ruolo=utente_db['Ruolo']
    )

    login_user(utente, remember=remember_me)

    return redirect(url_for('homepage'))

# FUNZIONI PERFORMANCES 

@app.route('/insert-performance', methods=['POST'])
@login_required
def insert_performance():
    # Raccogli i dati dal form modale performance
    artista = request.form.get('artista')

    if not artista:
        performances = performances_dao.get_performances_by_organizer(current_user.id)
        for performance in performances:
            immagini = immagini_dao.get_images_by_performance_id(performance['ID'])
            performance['Immagine'] = immagini[0] if immagini else None
        return render_template('profile.html', error_message="Inserisci un artista!", 
                               p_ruolo=ruoli_dao.get_role_by_id(current_user.ruolo)[0], p_palchi=palchi_dao.get_all_stages(),
                               p_performances_list=performances)

    # Controlla se l'artista ha gia una performance registrata
    artisti_registrati = [a[0] for a in performances_dao.get_artists_of_performances()]
    if artista in artisti_registrati:
        performances = performances_dao.get_performances_by_organizer(current_user.id)
        for performance in performances:
            immagini = immagini_dao.get_images_by_performance_id(performance['ID'])
            performance['Immagine'] = immagini[0] if immagini else None
        return render_template('profile.html', error_message="Artista già registrato con una performance!", 
                               p_ruolo=ruoli_dao.get_role_by_id(current_user.ruolo)[0], p_palchi=palchi_dao.get_all_stages(),
                               p_performances_list=performances)

    giorno_inizio = request.form.get('giorno_inizio')
    ora_inizio = request.form.get('ora_inizio')
    durata = request.form.get('durata')
    descrizione = request.form.get('descrizione')
    palco = request.form.get('palco') #id del palco
    genere = request.form.get('genere')
    pubblicata = True if request.form.get('pubblicata') == 'on' else False

    if not giorno_inizio or not ora_inizio or not durata or not descrizione or not palco or not genere:
        performances = performances_dao.get_performances_by_organizer(current_user.id)
        for performance in performances:
            immagini = immagini_dao.get_images_by_performance_id(performance['ID'])
            performance['Immagine'] = immagini[0] if immagini else None
        return render_template('profile.html', error_message="Tutti i campi sono obbligatori!", 
                               p_ruolo=ruoli_dao.get_role_by_id(current_user.ruolo)[0], p_palchi=palchi_dao.get_all_stages(),
                               p_performances_list=performances)

    # Recupera tutte le performance pubbliche (per tutti gli organizzatori)
    all_performances = performances_dao.get_all_performances()
    if performance_is_overlapping(all_performances, giorno_inizio, ora_inizio, durata, palco):
        performances = performances_dao.get_performances_by_organizer(current_user.id)
        for performance in performances:
            immagini = immagini_dao.get_images_by_performance_id(performance['ID'])
            performance['Immagine'] = immagini[0] if immagini else None
        return render_template('profile.html', error_message="Sovrapposizione con un'altra performance pubblicata sullo stesso palco e giorno!", 
                               p_ruolo=ruoli_dao.get_role_by_id(current_user.ruolo)[0], p_palchi=palchi_dao.get_all_stages(),
                               p_performances_list=performances)

    # Inserisci i dati nella tabella Performances, aggiungendo l'OrganizzatoreID
    performance_data = (artista, giorno_inizio, ora_inizio, durata, descrizione, palco, genere, pubblicata, current_user.id)
    performances_dao.insert_performance(performance_data)

    immagini = request.files.getlist('performanceImages')
    immagini_url = []

    if not immagini:
        # Se non sono state caricate immagini, reindirizza alla pagina del profilo
        performances = performances_dao.get_performances_by_organizer(current_user.id)
        for performance in performances:
            immagini = immagini_dao.get_images_by_performance_id(performance['ID'])
            performance['Immagine'] = immagini[0] if immagini else None
        return render_template('profile.html', error_message="Inserisci almeno un'immagine!", 
                               p_ruolo=ruoli_dao.get_role_by_id(current_user.ruolo)[0], p_palchi=palchi_dao.get_all_stages(),
                               p_performances_list=performances)

    # Salva le immagini nella cartella 'static/performances-images'
    for img in immagini:
        if img and img.filename:
            estensione = img.filename.split('.')[-1].lower()
            solo_nome = img.filename.split('.')[0]
            image_name = f"performance_{artista}_{performances_dao.get_perf_id_from_artist(artista)}_{solo_nome}.{estensione}"
            img.save(f'FestivalMusicale/static/performances-images/{image_name}')
            immagini_url.append(f'FestivalMusicale/static/performances-images/{image_name}')

    # Inserisci le immaigni nel DB
    performace_id = performances_dao.get_perf_id_from_artist(artista)
    immagini_dao.insert_images(immagini_url, performace_id)

    return redirect(url_for('profile'))

@app.route('/edit-performance/<int:performance_id>', methods=['POST'])
@login_required
def edit_performance(performance_id):
    artista = request.form.get('artista')
    giorno_inizio = request.form.get('giorno_inizio')
    ora_inizio = request.form.get('ora_inizio')
    durata = request.form.get('durata')
    descrizione = request.form.get('descrizione')
    palco = request.form.get('palco')  # id del palco
    genere = request.form.get('genere')

    if not artista or not giorno_inizio or not ora_inizio or not durata or not descrizione or not palco or not genere:
        perf = performances_dao.get_performance_by_id(performance_id)
        immagini = immagini_dao.get_images_by_performance_id(performance_id)
        palchi = palchi_dao.get_all_stages()
        return render_template('performance.html', p_immagini=immagini, p_performance=perf, p_edit=True, p_palchi=palchi, 
            error_message="Tutti i campi sono obbligatori!")

    # Recupera tutte le performance pubbliche (per tutti gli organizzatori)
    all_performances = performances_dao.get_all_performances()
    if performance_is_overlapping(all_performances, giorno_inizio, ora_inizio, durata, palco, exclude_id=performance_id):
        perf = performances_dao.get_performance_by_id(performance_id)
        immagini = immagini_dao.get_images_by_performance_id(performance_id)
        palchi = palchi_dao.get_all_stages()
        return render_template('performance.html', p_immagini=immagini, p_performance=perf, p_edit=True, p_palchi=palchi, 
            error_message="Sovrapposizione con un'altra performance pubblicata sullo stesso palco e giorno!")

    # Aggiorna la performance nel DB
    performances_dao.update_performance(performance_id, artista, giorno_inizio, 
                                        ora_inizio, durata, descrizione, palco, genere)

    return redirect(url_for('performance', performance_id=performance_id))

@app.route('/post-performance/<int:performance_id>', methods=['POST'])
@login_required
def post_performance(performance_id):
    perf = performances_dao.get_performance_by_id(performance_id)
    # Recupera tutte le performance pubbliche (per tutti gli organizzatori)
    all_performances = performances_dao.get_all_performances()
    if performance_is_overlapping(all_performances, perf['GiornoInizio'], perf['OraInizio'], perf['Durata'], perf['Palco'], exclude_id=performance_id):
        immagini = immagini_dao.get_images_by_performance_id(performance_id)
        palchi = palchi_dao.get_all_stages()
        return render_template('performance.html', p_immagini=immagini, p_performance=perf, p_edit=True, p_palchi=palchi, 
            error_message="Sovrapposizione con un'altra performance pubblicata sullo stesso palco e giorno!")
    performances_dao.set_performance_published(performance_id)
    return redirect(url_for('performance', performance_id=performance_id))

@app.route('/add-performance-images/<int:performance_id>', methods=['POST'])
@login_required
def add_performance_images(performance_id):
    immagini = request.files.getlist('performanceImages')
    immagini_url = []

    if not immagini:
        # Se non sono state caricate immagini, reindirizza alla pagina della performance
        return redirect(url_for('performance', performance_id=performance_id))

    # Salva le immagini nella cartella 'static/performances-images'
    for img in immagini:
        if img and img.filename:
            estensione = img.filename.split('.')[-1].lower()
            solo_nome = img.filename.split('.')[0]
            image_name = f"performance_{performance_id}_{solo_nome}.{estensione}"
            img.save(f'FestivalMusicale/static/performances-images/{image_name}')
            immagini_url.append(f'FestivalMusicale/static/performances-images/{image_name}')

    # Inserisci le immagini nel DB
    immagini_dao.insert_images(immagini_url, performance_id)

    return redirect(url_for('performance', performance_id=performance_id))

@app.route('/delete-performance-image/<int:performance_id>', methods=['POST'])
@login_required
def delete_performance_image(performance_id):
    url = request.form.get('image_url')

    if not url:
        # Se non è stata fornita un'URL, reindirizza alla pagina della performance
        return redirect(url_for('performance', performance_id=performance_id))

    # Rimuovi l'immagine dal DB
    immagini_dao.delete_image_by_url(url)
    # Rimuovi l'immagine dal filesystem
    if os.path.exists(url):
        os.remove(url)
    return redirect(url_for('performance', performance_id=performance_id))

@app.route('/remove-performance/<int:performance_id>', methods=['POST'])
@login_required
def remove_performance(performance_id):
    # Rimuovi la performance dal DB
    performances_dao.delete_performance(performance_id)

    # Rimuovi le immagini associate alla performance
    immagini = immagini_dao.get_images_by_performance_id(performance_id)
    for img in immagini:
        if os.path.exists(img):
            os.remove(img)
        immagini_dao.delete_image_by_url(img)

    return redirect(url_for('profile'))

def to_minutes(ora):
    h, m = map(int, ora.split(":"))
    return h * 60 + m

def performance_is_overlapping(performance_list, giorno_inizio, ora_inizio, durata, palco,exclude_id=None):
    start_new = to_minutes(ora_inizio)
    end_new = start_new + int(durata)
    for perf in performance_list:
        if perf['Pubblicata'] != 1:
            continue
        if perf['GiornoInizio'] != giorno_inizio or str(perf['Palco']) != str(palco):
            continue
        if exclude_id and str(perf['ID']) == str(exclude_id):
            continue
        start = to_minutes(perf['OraInizio'])
        end = start + int(perf['Durata'])
        if start < end_new and end > start_new:
            return True
    return False

# FUNZIONI ACQUISTO TICKETS

@app.route('/buy-ticket-redirect', methods=['POST'])
@login_required
def buy_ticket():
    p_pass = request.form.get("p_pass")

    if not p_pass:
        return render_template('buy_ticket.html', p_utente=current_user, error_message="Seleziona un tipo di pass!")

    if (p_pass == "daily" or p_pass == "2days"):
        days = request.form.get("days")
    else:
        days = "venerdi-sabato-domenica"

    if (utenti_dao.get_ticket_by_user_id(current_user.id)):
        return render_template('profile.html', p_ruolo=ruoli_dao.get_role_by_id(current_user.ruolo)[0],
                               error_message="Hai gia acquistato un biglietto per questo evento!",
                               p_ticket=tickets_dao.get_ticket_by_id(utenti_dao.get_ticket_by_user_id(current_user.id)))
    if (current_user.ruolo == 2):
        perf_list = performances_dao.get_performances_ordered()
        perf_list = [p for p in perf_list if p['Pubblicata'] == 1]  # Filtra solo le performance pubblicate
        for performance in perf_list:
            # Ottengo la prima immagine associata alla performance
            immagini = immagini_dao.get_images_by_performance_id(performance['ID'])
            performance['Immagine'] = immagini[0] if immagini else None
            # Ottengo il nome del palco associato alla performance
            performance['Palco'] = palchi_dao.get_stage_name_by_id(performance['Palco'])

        # prendi solo il nome del palco (numero 1 nella tupla)
        palchi = [p[1] for p in palchi_dao.get_all_stages()]
        generi = performances_dao.get_all_genres_of_public_performances()
        
        return render_template('homepage.html', p_performances_list=perf_list,
                                p_palchi=palchi, p_generi=generi, p_message="Non puoi acquistare biglietti come organizzatore!")
                               
    return render_template('buy_ticket.html', p_pass=p_pass, p_days=days,
                           p_utente=current_user)
    
@app.route('/buy-ticket-confirm', methods=['POST'])
@login_required
def buy_ticket_confirm():
    global ticket_venerdi, ticket_sabato, ticket_domenica
    pass_type = request.form.get("cart_pass")
    days = request.form.get("cart_desc").split('-')

    if not pass_type or not days:
        return render_template('buy_ticket.html', p_utente=current_user, error_message="Seleziona un tipo di pass e i giorni!")
    
    if pass_type == "daily":
        if days[0] == "venerdi":
            ticket_venerdi -= 1
        elif days[0] == "sabato":
            ticket_sabato -= 1
        elif days[0] == "domenica":
            ticket_domenica -= 1
        ticket_id = tickets_dao.insert_ticket_daily(pass_type, days[0])
    elif pass_type == "2days":
        if days[0] == "venerdi" and days[1] == "sabato":
            ticket_venerdi -= 1
            ticket_sabato -= 1
        elif days[0] == "sabato" and days[1] == "domenica":
            ticket_sabato -= 1
            ticket_domenica -= 1
        ticket_id =tickets_dao.insert_ticket_2days(pass_type, days[0], days[1])
    else:
        ticket_venerdi -= 1
        ticket_sabato -= 1
        ticket_domenica -= 1
        ticket_id =tickets_dao.insert_ticket_full(pass_type, days[0], days[1], days[2])

    utenti_dao.connect_ticket_to_user(ticket_id, current_user.id)

    return render_template('profile.html', p_ruolo=ruoli_dao.get_role_by_id(current_user.ruolo)[0],
                           p_ticket=tickets_dao.get_ticket_by_id(ticket_id))

# FUNZIONI PER IL CONTATTO
@app.route('/send-contact-form', methods=['POST'])
def send_contact_form():
    return render_template('contacts.html', p_message="Messaggio inviato con successo!")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)