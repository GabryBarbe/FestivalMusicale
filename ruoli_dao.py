import sqlite3

def get_all_roles():
    query = "SELECT * FROM Ruoli"

    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query)

    roles = cursor.fetchall()

    conn.close()

    return roles

def get_role_by_id(role_id):
    query = "SELECT Ruolo FROM Ruoli WHERE ID = ?"

    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (role_id,))

    role = cursor.fetchone()

    conn.close()

    return role
