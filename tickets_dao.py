import sqlite3

def insert_ticket_daily(tipo, giorno1):
    query = "INSERT INTO Tickets (Tipologia, Giorno1) VALUES (?, ?)"

    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (tipo, giorno1))
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return ticket_id

def insert_ticket_2days(tipo, giorno1, giorno2):
    query = "INSERT INTO Tickets (Tipologia, Giorno1, Giorno2) VALUES (?, ?, ?)"

    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (tipo, giorno1, giorno2))
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return ticket_id

def insert_ticket_full(tipo, giorno1, giorno2, giorno3):
    query = "INSERT INTO Tickets (Tipologia, Giorno1, Giorno2, Giorno3) VALUES (?, ?, ?, ?)"

    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (tipo, giorno1, giorno2, giorno3))
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return ticket_id

def get_ticket_number_venerdi():
    query = "SELECT COUNT(*) FROM Tickets WHERE Giorno1 = 'venerdi' OR Giorno2 = 'venerdi' OR Giorno3 = 'venerdi'"

    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query)
    count = cursor.fetchone()[0]
    conn.close()

    return count

def get_ticket_number_sabato():
    query = "SELECT COUNT(*) FROM Tickets WHERE Giorno1 = 'sabato' OR Giorno2 = 'sabato' OR Giorno3 = 'sabato'"

    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query)
    count = cursor.fetchone()[0]
    conn.close()

    return count

def get_ticket_number_domenica():
    query = "SELECT COUNT(*) FROM Tickets WHERE Giorno1 = 'domenica' OR Giorno2 = 'domenica' OR Giorno3 = 'domenica'"

    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query)
    count = cursor.fetchone()[0]
    conn.close()

    return count

def get_ticket_by_id(ticket_id):
    query = "SELECT * FROM Tickets WHERE ID = ?"

    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (ticket_id,))

    ticket_data = cursor.fetchone()
    conn.close()

    if ticket_data:
        return {
            'ID': ticket_data[0],
            'Tipologia': ticket_data[1],
            'Giorno1': ticket_data[2],
            'Giorno2': ticket_data[3],
            'Giorno3': ticket_data[4]
        }

    return None