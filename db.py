import sqlite3
from time import time
from operator import itemgetter

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


def increment_votes(image_id):
    connection, cursor = connect()

    cursor.execute(
        "UPDATE images SET voted = voted + 1 WHERE imageID = ?", (image_id,))

    close(connection)


def increment_ranking(image_id):
    connection, cursor = connect()

    cursor.execute(
        "UPDATE images SET ranking = ranking + 1 WHERE imageID = ?", (image_id,))

    close(connection)


def get_bottom_voted():
    connection, cursor = connect()

    cursor.execute(
        "SELECT creature, imageID, voted, ranking, userID FROM images")
    results = cursor.fetchall()

    bottom_voted = sorted(results, key=itemgetter(2))
    bottom_voted = bottom_voted[:len(bottom_voted)//2]

    close(connection)
    return bottom_voted


def get_userID(image_id):
    connection, cursor = connect()

    cursor.execute("SELECT userID FROM images WHERE imageID=?", (image_id,))
    result = cursor.fetchone()

    user_id = result[0] if result else None

    close(connection)
    return user_id


def get_all_image_ids():
    connection, cursor = connect()

    cursor.execute("SELECT imageID FROM images")
    results = cursor.fetchall()

    image_ids = results

    close(connection)
    return image_ids


def get_image_ids_by_creature(creature):
    connection, cursor = connect()

    cursor.execute("SELECT imageID FROM images WHERE creature=?", (creature,))
    results = cursor.fetchall()

    close(connection)
    return results


def get_all_creatures():
    connection, cursor = connect()

    cursor.execute("SELECT DISTINCT creature FROM images")
    results = cursor.fetchall()

    close(connection)
    return results


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


def api_key_access(request, sqllogic, sqlparams):
    #if not verify_apikey(api_key):
    #    return "Invalid API key"

    connection, cursor = connect()

    if request == "get_image_data":
        cursor.execute(f"SELECT * FROM images WHERE {sqllogic}", sqlparams)
        
        results = cursor.fetchall()
        close(connection)
        for creature in range(len(results)):
            results[creature] = {
                "creature": results[creature][0],
                "imageID": results[creature][1],
                "userID": results[creature][2],
                "time": results[creature][3],
                "ranking": results[creature][4],
                "voted": results[creature][5]
            }
        return results

    close(connection)
    return "Invalid Request"

if __name__ == "__main__":
    connection, cursor = connect()

    cursor.execute("""SELECT * FROM images WHERE "owlbear" IN (creature, "")""")
    print(cursor.fetchall())
    close(connection)