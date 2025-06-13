import sqlite3

def get_all_stages():
    query = "SELECT * FROM Palchi"

    conn = sqlite3.connect('sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query)

    palchi = cursor.fetchall()

    conn.close()

    return palchi

def get_stage_name_by_id(stage_id):
    query = "SELECT NomePalco FROM Palchi WHERE ID = ?"

    conn = sqlite3.connect('sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (stage_id,))

    stage_name = cursor.fetchone()

    conn.close()

    return stage_name[0] if stage_name else None