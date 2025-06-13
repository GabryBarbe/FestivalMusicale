import sqlite3

def insert_performance(data):
    query = """
        INSERT INTO Performances 
        (Artista, GiornoInizio, OraInizio, Durata, DescrizioneBreve, Palco, GenereMusicale, Pubblicata, OrganizzatoreID)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, data)
    
    conn.commit()
    conn.close()

def get_perf_id_from_artist(artista):
    query = "SELECT ID FROM Performances WHERE Artista = ?"

    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (artista,))

    result = cursor.fetchone()

    conn.close()
    if result:
        return result[0]
    return None

def get_artists_of_performances():
    query = "SELECT Artista FROM Performances"

    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query)

    artists = cursor.fetchall()

    conn.close()

    return artists

def get_performance_by_id(perf_id):
    query = "SELECT * FROM Performances WHERE ID = ?"

    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (perf_id,))

    performance = cursor.fetchone()

    conn.close()

    if performance:
        return {
            'ID': performance[0],
            'Artista': performance[1],
            'GiornoInizio': performance[2],
            'OraInizio': performance[3],
            'Durata': performance[4],
            'DescrizioneBreve': performance[5],
            'Palco': performance[6],
            'GenereMusicale': performance[7],
            'Pubblicata': performance[8],
            'OrganizzatoreID': performance[9]
        }
    
    return None

def get_performances_by_organizer(organizer_id):
    query = "SELECT * FROM Performances WHERE OrganizzatoreID = ?"
    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (organizer_id,))
    performances = cursor.fetchall()
    conn.close()
    # Restituisce una lista di dizionari come get_performance_by_id
    result = []
    for p in performances:
        result.append({
            'ID': p[0],
            'Artista': p[1],
            'GiornoInizio': p[2],
            'OraInizio': p[3],
            'Durata': p[4],
            'DescrizioneBreve': p[5],
            'Palco': p[6],
            'GenereMusicale': p[7],
            'Pubblicata': p[8],
            'OrganizzatoreID': p[9]
        })
    return result

def update_performance(performance_id, artista, giorno_inizio, ora_inizio, durata, descrizione, palco, genere):
    query = """
        UPDATE Performances 
        SET Artista = ?, GiornoInizio = ?, OraInizio = ?, Durata = ?, DescrizioneBreve = ?, Palco = ?, GenereMusicale = ?
        WHERE ID = ?
    """
    
    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (artista, giorno_inizio, ora_inizio, durata, descrizione, palco, genere, performance_id))
    
    conn.commit()
    conn.close()

def set_performance_published(performance_id):
    query = "UPDATE Performances SET Pubblicata = 1 WHERE ID = ?"
    
    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (performance_id,))
    
    conn.commit()
    conn.close()

def delete_performance(performance_id):
    query = "DELETE FROM Performances WHERE ID = ?"
    
    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (performance_id,))
    
    conn.commit()
    conn.close()

def get_all_performances():
    query = "SELECT * FROM Performances"

    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query)

    performances = cursor.fetchall()
    conn.close()

    result = []
    for p in performances:
        result.append({
            'ID': p[0],
            'Artista': p[1],
            'GiornoInizio': p[2],
            'OraInizio': p[3],
            'Durata': p[4],
            'DescrizioneBreve': p[5],
            'Palco': p[6],
            'GenereMusicale': p[7],
            'Pubblicata': p[8],
            'OrganizzatoreID': p[9]
        })
    return result

def get_all_public_performances():
    query = "SELECT * FROM Performances WHERE Pubblicata = 1"

    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query)

    performances = cursor.fetchall()
    conn.close()
    
    result = []
    for p in performances:
        result.append({
            'ID': p[0],
            'Artista': p[1],
            'GiornoInizio': p[2],
            'OraInizio': p[3],
            'Durata': p[4],
            'DescrizioneBreve': p[5],
            'Palco': p[6],
            'GenereMusicale': p[7],
            'Pubblicata': p[8],
            'OrganizzatoreID': p[9]
        })
    return result

def get_draft_performances_by_organizer(organizer_id):
    query = "SELECT * FROM Performances WHERE OrganizzatoreID = ? AND Pubblicata = 0"

    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (organizer_id,))
    
    performances = cursor.fetchall()
    conn.close()
    
    result = []
    for p in performances:
        result.append({
            'ID': p[0],
            'Artista': p[1],
            'GiornoInizio': p[2],
            'OraInizio': p[3],
            'Durata': p[4],
            'DescrizioneBreve': p[5],
            'Palco': p[6],
            'GenereMusicale': p[7],
            'Pubblicata': p[8],
            'OrganizzatoreID': p[9]
        })
    return result

def get_performances_ordered():
    # Ordina le performace per giorno crescente del tipo venerdi, sabato domenica
    # e non in ordine alfabetico (sarebbe sbagliato)
    # dopo ora di inizio
    query = """
    SELECT * FROM Performances 
    ORDER BY 
        CASE GiornoInizio
            WHEN 'venerdi' THEN 1
            WHEN 'sabato' THEN 2
            WHEN 'domenica' THEN 3
            ELSE 4
        END,
        OraInizio
    """
    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query)
    performances = cursor.fetchall()
    conn.close()
    result = []
    for p in performances:
        result.append({
            'ID': p[0],
            'Artista': p[1],
            'GiornoInizio': p[2],
            'OraInizio': p[3],
            'Durata': p[4],
            'DescrizioneBreve': p[5],
            'Palco': p[6],
            'GenereMusicale': p[7],
            'Pubblicata': p[8],
            'OrganizzatoreID': p[9]
        })
    return result

def get_all_genres_of_public_performances():
    query = "SELECT DISTINCT GenereMusicale FROM Performances WHERE Pubblicata = 1"
    
    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query)
    
    genres = cursor.fetchall()
    
    conn.close()
    
    return [genre[0] for genre in genres] if genres else []