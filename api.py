import db
import orjson
import os
from flask import Flask, request, send_file

host = "0.0.0.0"
port = "8080"

app = Flask(__name__)

errors = {
    "Invalid API key": (orjson.dumps({"error": "Invalid API key"}), 401),
    "Missing Authorization header": (orjson.dumps({"error": "Missing Authorization header"}), 400),
    "Not Valid Creature": (orjson.dumps({"error": "Not Valid Creature"}), 400),
    "Not Valid imageID": (orjson.dumps({"error": "Not Valid imageID"}), 400),
    "Invalid Request": (orjson.dumps({"error": "Invalid Request"}), 400),
    "Unauthorized": (orjson.dumps({"error": "Unauthorized"}), 401),
    "Forbidden": (orjson.dumps({"error": "Forbidden"}), 403),
    "Not Found": (orjson.dumps({"error": "Not Found"}), 404),
}


@app.get('/api/image_data')
def image_data():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return errors['Missing Authorization header']
    
    if not db.verify_apikey(auth_header):
        return errors['Invalid API key']

    data = request.get_json()
    creature = data.get('creature')
    image_id = data.get('imageID')
    user_id = data.get('userID')

    result_data = db.api_key_access(
        auth_header, "get_image_data", creature, image_id, user_id)

    results = {
        "count":len(result_data),
        "data":result_data
    }

    return results


@app.get('/api/get_image_ids')
def get_image_ids():
    data = db.get_all_image_ids()
    results = {
        "count":len(data),
        "data":data
    }
    return results


@app.get("/api/get_image", defaults={"creature":"","imageID": ""})
@app.get("/api/get_image/<creature>",defaults={"imageID":""})
@app.get("/api/get_image/<creature>/<imageID>")
def get_image(creature, imageID):
    if creature == "":
        creaturelist = db.get_all_creatures()
        results = {
            "count":len(creaturelist),
            "data":creaturelist
        }

        return orjson.dumps(results)
    
    if creature not in db.get_all_creatures():
        return errors["Not Valid Creature"]
    
    if imageID == "":
        IDlist = db.get_image_ids_by_creature(creature)
        results = {
            "count": len(IDlist),
            "data": [ID.replace(".jpg","") for ID in IDlist]
        }

        return orjson.dumps(results)

    if f"{imageID}.jpg" not in db.get_image_ids_by_creature(creature):
        realcreature = db.get_creature(imageID)
        if realcreature is None:
            return errors["Not Valid imageID"]
        return orjson.dumps({"error": "ID found elsewhere", "location": realcreature}), 400

    return send_file(os.path.join("images",creature,f"{imageID}.jpg"))

app.run(host, port)
