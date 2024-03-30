import sqlite3
from time import time
from operator import itemgetter

def connect() -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    """Connect to the SQLite database file and return a connection and cursor.

    Returns:
        tuple[sqlite3.Connection, sqlite3.Cursor]: The SQLite database connection and cursor.
    """
    connection = sqlite3.connect("database/images.db")
    cursor = connection.cursor()
    return connection, cursor


def close(connection:sqlite3.Connection):
    """
    Commits changes to the database file and closes the connection.
    """
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

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS suggestions(
        suggestion STR,
        userID INT,
        time INT
        )"""
    )
    
        
          
    close(connection)

init()

    
def send_suggestion(suggestion:str, user_id:int):
    """
    Inserts a new suggestion into the suggestions table.
    
    Args:
        suggestion (str): The text of the suggestion.
        user_id (int): The ID of the user making the suggestion.
        
    The current time is inserted along with the suggestion and user ID.
    """
    connection, cursor = connect()

    cursor.execute("INSERT INTO suggestions VALUES (?, ?, ?)",
                   (suggestion, user_id, int(time())))

    close(connection)


def add_image(creature: str, image_ID: str, userID: int) -> None:
    """Adds a new image to the images table.

    Args:
        creature (str): The name of the creature in the image. 
        image_ID (str): The unique ID of the image.
        userID (int): The ID of the user uploading the image.
        
    Inserts the image info into the images table along with the current timestamp.
    """
    connection, cursor = connect()

    cursor.execute("INSERT INTO images VALUES (?, ?, ?, ?, 0, 0)",
                   (creature, image_ID, userID, int(time())))

    close(connection)


def add_apikey(key: str, user_id: int, name: str) -> None:
    """
    Inserts a new API key into the apikeys table.

    Args:
        key (str): The API key string. 
        user_id (int): The ID of the user the key belongs to.
        name (str): A name for the key.

    Inserts the key info into the apikeys table along with the current timestamp.
    """
    connection, cursor = connect()

    cursor.execute("INSERT INTO apikeys VALUES (?, ?, ?, ?)",
                   (key, user_id, name, int(time())))

    close(connection)


def get_creature(image_id: str) -> str:
    """Gets the creature name for the given image ID.

    Args:
        image_id (str): The ID of the image to look up.

    Returns:
        str: The name of the creature in the image, or None if not found.
    """
    connection, cursor = connect()

    cursor.execute("SELECT creature FROM images WHERE imageID=?", (image_id,))
    result = cursor.fetchone()

    creature = result[0] if result else None

    close(connection)
    return creature


def increment_votes(image_id: str) -> None:
    """
    Increments the vote count for the given image ID in the images table.

    Args:
        image_id (str): The ID of the image to increment votes for.

    Returns:
        None
    """
    connection, cursor = connect()

    cursor.execute(
        "UPDATE images SET voted = voted + 1 WHERE imageID = ?", (image_id,))

    close(connection)


def increment_ranking(image_id: str) -> None:
    """
    Increments the ranking for the image with the given ID in the images table.

    Args:
        image_id (str): The ID of the image to increment the ranking for.

    Returns:
        None
    """
    connection, cursor = connect()

    cursor.execute(
        "UPDATE images SET ranking = ranking + 1 WHERE imageID = ?", (image_id,))

    close(connection)


def get_bottom_voted() -> list:
    """
    Returns a list of the bottom half of images sorted by lowest vote count.

    Connects to the database, selects creature, imageID, votes, ranking, and userID 
    from the images table, sorts the results by lowest vote count, and returns the
    bottom half of the sorted results.
    """
    connection, cursor = connect()

    cursor.execute(
        "SELECT creature, imageID, voted, ranking, userID FROM images")
    results = cursor.fetchall()

    bottom_voted = sorted(results, key=itemgetter(2))
    bottom_voted = bottom_voted[:len(bottom_voted)//2]

    close(connection)
    return bottom_voted


def get_userID(image_id: str) -> int:
    """
    Retrieves the userID for the image with the given imageID.
    
    Connects to the database, queries the userID from the images table 
    where the imageID matches the provided imageID, and returns the userID.
    Returns None if no matching imageID is found.
    """
    connection, cursor = connect()

    cursor.execute("SELECT userID FROM images WHERE imageID=?", (image_id,))
    result = cursor.fetchone()

    user_id = result[0] if result else None

    close(connection)
    return user_id


def get_all_image_ids() -> list:
    """
    Retrieves a list of all imageIDs from the images table.
    
    Connects to the database, selects all imageIDs from the images table, 
    stores them in a list, closes the connection, and returns the list.
    """
    connection, cursor = connect()

    cursor.execute("SELECT imageID FROM images")
    results = cursor.fetchall()

    image_ids = results

    close(connection)
    return image_ids


def get_image_ids_by_creature(creature: str) -> list:
    """
    Retrieves a list of imageIDs for images of the given creature from the images table.
    
    Connects to the database, selects the imageIDs from the images table 
    where the creature matches the provided creature, stores them in a list,
    closes the connection, and returns the list.
    """
    connection, cursor = connect()

    cursor.execute("SELECT imageID FROM images WHERE creature=?", (creature,))
    results = cursor.fetchall()

    close(connection)
    return results


def get_all_creatures() -> list:
    """
    Retrieves a list of all distinct creatures from the images table.
    
    Connects to the database, selects the distinct creatures from the 
    images table, closes the connection, and returns the list.
    """
    connection, cursor = connect()

    cursor.execute("SELECT DISTINCT creature FROM images")
    results = cursor.fetchall()

    close(connection)
    return results


def revoke_apikeys(user_id: int) -> None:
    """
    Revokes all API keys for the given user by deleting the user's rows from 
    the apikeys table.
    
    Args:
        user_id (int): The ID of the user to revoke API keys for.
        
    """
    connection, cursor = connect()

    cursor.execute("DELETE FROM apikeys WHERE userID=?", (user_id,))

    close(connection)


def verify_apikey(api_key: str) -> bool:
    """Verifies if an API key is valid by checking if it exists in the apikeys table.

    Args:
        api_key (str): The API key to verify.
        
    Returns:
        bool: True if the API key is valid, False otherwise.
    """
    connection, cursor = connect()

    cursor.execute("SELECT * FROM apikeys WHERE key=?", (api_key,))
    result = cursor.fetchone()

    valid = result is not None

    close(connection)
    return valid


def api_key_access(request: str, sqllogic: str, sqlparams: tuple):
    """
    api_key_access provides access to the database.

    It takes in a request string indicating the type of query, an SQL WHERE clause logic string, 
    and the parameters to use in the WHERE clause.

    Based on the request, it will query the database and return the results.

    Valid requests are "get_image_data" and "suggestions". Any other request will return an error.
    """
    # if not verify_apikey(api_key):
    #    return "Invalid API key"

    connection, cursor = connect()

    if not isinstance(sqlparams, tuple):
        sqlparams = (sqlparams,)

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

    elif request == "suggestions":
        cursor.execute(
            f"SELECT * FROM suggestions WHERE {sqllogic}", sqlparams)

        results = cursor.fetchall()
        close(connection)
        for suggestion in range(len(results)):
            results[suggestion] = {
                "suggestion": results[suggestion][0],
                "userID": results[suggestion][1],
                "time": results[suggestion][2]
            }
        return results

    close(connection)
    return "Invalid Request"


if __name__ == "__main__":
    connection, cursor = connect()

    cursor.execute("""SELECT * FROM images WHERE "owlbear" IN (creature, "")""")
    print(cursor.fetchall())
    close(connection)