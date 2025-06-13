import sqlite3

def get_emails_of_registered_users():
    query = "SELECT Email FROM Utenti"

    conn = sqlite3.connect('sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query)

    emails = [row[0] for row in cursor.fetchall()]

    conn.close()
    
    return emails

def get_password_from_email(email):
    query = "SELECT Password FROM Utenti WHERE Email = ?"

    conn = sqlite3.connect('sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (email,))

    passw = cursor.fetchone()

    conn.close()

    return passw[0] if passw else None

def get_user_by_email(email):
    query = "SELECT * FROM Utenti WHERE Email = ?"

    conn = sqlite3.connect('sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (email,))

    user_data = cursor.fetchone()

    conn.close()

    if user_data:
        return {
            'ID': user_data[0],
            'Nome': user_data[1],
            'Cognome': user_data[2],
            'Email': user_data[3],
            'Password': user_data[4],
            'Ruolo': user_data[5]
        }
    
    return None

def get_user_by_id(user_id):
    query = "SELECT * FROM Utenti WHERE ID = ?"

    conn = sqlite3.connect('sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (user_id,))

    user_data = cursor.fetchone()

    conn.close()

    if user_data:
        return {
            'id': user_data[0],
            'nome': user_data[1],
            'cognome': user_data[2],
            'email': user_data[3],
            'password': user_data[4],
            'ruolo': user_data[5]
        }
    
    return None

def insert_user(user_data):
    query = "INSERT INTO Utenti (Nome, Cognome, Email, Password, Ruolo) VALUES (?, ?, ?, ?, ?)"

    conn = sqlite3.connect('sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (user_data['nome'], user_data['cognome'], user_data['email'], user_data['password'], user_data['ruolo']))

    conn.commit()
    conn.close()

def get_performances_by_user_id(user_id):
    query = "SELECT PerformanceID FROM Utenti WHERE ID = ?"

    conn = sqlite3.connect('sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (user_id,))

    performances = cursor.fetchall()

    conn.close()

    return performances if performances else None

def connect_ticket_to_user(ticket_id, user_id):
    query = "UPDATE Utenti SET TicketID = ? WHERE ID = ?"

    conn = sqlite3.connect('sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (ticket_id, user_id))

    conn.commit()
    conn.close()

def get_ticket_by_user_id(user_id):
    query = "SELECT TicketID FROM Utenti WHERE ID = ?"

    conn = sqlite3.connect('sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (user_id,))

    ticket_id = cursor.fetchone()

    conn.close()

    return ticket_id[0] if ticket_id else None