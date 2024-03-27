import sqlite3
from time import time

def connect():
    connection = sqlite3.connect("database/images.db")
    cursor = connection.cursor()
    return connection, cursor

def close(connection):
    connection.commit()
    connection.close()

def init():
    connection, cursor = connect()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS images(
        creature STR,
        imageID STR,
        userID INT,
        time INT,
        ranking INT,
        voted INT
        )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS apikeys(
        key STR, 
        userID INT,
        name STR,
        time INT
        )"""
    )
          
    close(connection)

init()

def add_image(creature, image_ID, userID) -> None:
    connection, cursor = connect()

    cursor.execute("INSERT INTO images VALUES (?, ?, ?, ?, 0, 0)",
                   (creature, image_ID, userID, int(time())))
    
    close(connection)
      
def add_apikey(key, user_id, name):
    connection, cursor = connect()

    cursor.execute("INSERT INTO apikeys VALUES (?, ?, ?, ?)",
                   (key, user_id, name, int(time())))

    close(connection)


def get_creature(image_id):
    connection, cursor = connect()

    cursor.execute("SELECT creature FROM images WHERE imageID=?", (image_id,))
    result = cursor.fetchone()

    creature = result[0] if result else None

    close(connection)
    return creature


def get_all_image_ids():
    connection, cursor = connect()

    cursor.execute("SELECT imageID FROM images")
    results = cursor.fetchall()

    image_ids = [result[0] for result in results]

    close(connection)
    return image_ids


def revoke_apikeys(user_id):
    connection, cursor = connect()

    cursor.execute("DELETE FROM apikeys WHERE userID=?", (user_id,))

    close(connection)


def verify_apikey(api_key):
    connection, cursor = connect()

    cursor.execute("SELECT * FROM apikeys WHERE key=?", (api_key,))
    result = cursor.fetchone()

    valid = result is not None

    close(connection)
    return valid


def api_key_access(api_key, request, creature="", image_id="", user_id=""):
    if not verify_apikey(api_key):
        return "Invalid API key"

    connection, cursor = connect()

    if request == "get_image_data":
        cursor.execute("SELECT * FROM images WHERE ? IN (creature, '') OR ? IN (imageID, '') OR ? IN (userID, '')",
                    (creature, image_id, user_id))
        
        result = cursor.fetchall()
        close(connection)
        return result

    close(connection)
    return "Invalid Request"

if __name__ == "__main__":
    connection, cursor = connect()

    cursor.execute("""SELECT * FROM images WHERE "owlbear" IN (creature, "")""")
    print(cursor.fetchall())
    close(connection)