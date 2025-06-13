import sqlite3

def insert_images(immagini, performance_id):
    query = "INSERT INTO ImmaginiPromozionali (PerformanceID, URL) VALUES (?, ?)"
    
    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    
    for immagine in immagini:
        cursor.execute(query, (performance_id, immagine))
    
    conn.commit()
    conn.close()

def get_images_by_performance_id(perf_id):
    query = "SELECT URL FROM ImmaginiPromozionali WHERE PerformanceID = ?"
    
    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (perf_id,))
    
    immagini = cursor.fetchall()
    
    conn.close()
    
    return [img[0] for img in immagini] if immagini else []

def delete_image_by_url(url):
    query = "DELETE FROM ImmaginiPromozionali WHERE URL = ?"
    
    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query, (url,))
    
    conn.commit()
    conn.close()

def get_all_images():
    query = "SELECT URL FROM ImmaginiPromozionali ORDER BY PerformanceID"
    
    conn = sqlite3.connect('FestivalMusicale/sunrift.db')
    cursor = conn.cursor()
    cursor.execute(query)
    
    immagini = cursor.fetchall()
    
    conn.close()
    
    return [img[0] for img in immagini] if immagini else []