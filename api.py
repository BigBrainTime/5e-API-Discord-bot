import db
import orjson
import os
from jsonsql import JsonSQL
from flask import Flask, request, send_file
from pydoc import locate

with open("config.json") as file:
    config = orjson.loads(file.read())
host = config["HOST"]
port = config["PORT"]
for column_type in config["allowed_columns"]:
    config["allowed_columns"][column_type] = locate(config["allowed_columns"][column_type])
jsonsql = JsonSQL(config['allowed_queries'], config['allowed_items'],
                  config['allowed_tables'], config['allowed_connections'], config['allowed_columns'])


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

@app.get('/api')
def api_home():
    endpoints = ["/get_image_ids","/get_image","/database"]
    return orjson.dumps(endpoints)


@app.get("/api/database", defaults={"table": ""})
@app.get('/api/database/<table>')
def image_data(table):
    #auth_header = request.headers.get('Authorization')
    #if not auth_header:
    #    return errors['Missing Authorization header']
    
    #if not db.verify_apikey(auth_header):
    #    return errors['Invalid API key']
    if table == "":
        return orjson.dumps(["/images","/suggestions"])

    data = request.get_json()
    basic_logic = data.get('logic')

    logic_results = jsonsql.logic_parse(basic_logic)
    if not logic_results[0]:
        return orjson.dumps({"JsonSQL error":logic_results[1]})
    sql_string, sql_params = logic_results[1:]

    if not isinstance(sql_params, tuple):
        sql_params = (sql_params,)

    result_data = db.api_key_access(table, sql_string, sql_params)

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
    creaturelist = [result[0] for result in db.get_all_creatures()]
    if creature == "":
        results = {
            "count":len(creaturelist),
            "data":creaturelist
        }

        return orjson.dumps(results)
    
    if creature not in creaturelist:
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
