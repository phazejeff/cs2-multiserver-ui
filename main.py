from flask import Flask, render_template, redirect, request, url_for, flash, jsonify
import subprocess
import asyncio
import time
import json
import os

app = Flask(__name__)
app.secret_key = 'suck my fat hairy sweaty balls, por favor'

PORT = 5000

MAPS = {
    "de_foroglio" : "3132854332",
    "de_lake" : "3219506727",
    "de_palais" : "3257582863",
    "de_eldorado" : "3408790618",
    "de_dogtown": "3414036782",
    "de_neptune" : "3430103877",
    "de_splat" : "3439120481"
}

SERVERS = [
    "game1",
    "game2",
    "game3",
    "game4"
]

@app.route("/")
def index():
    matches = os.listdir("matches")
    return render_template("index.html", maps=MAPS.keys(), servers=SERVERS, matches=matches)

@app.route("/start/<server>")
def start(server: str):
    map = request.args.get("map")
    if map and map in MAPS:
        subprocess.call(["cs2-server", f"@{server}", "start"])
        asyncio.run(changemap(server, map))
        flash(f"Started server {server} with map {map}")
    elif server in SERVERS:
        subprocess.call(["cs2-server", f"@{server}", "start"])
        flash(f"Started server {server}")
    return redirect(url_for("index"))

@app.route("/stop/<server>")
def stop(server: str):
    if server in SERVERS:
        subprocess.call(["cs2-server", f"@{server}", "stop"])
        flash(f"Stopped server {server}")
    return redirect(url_for("index"))

@app.route("/restart/<server>")
def restart(server: str):
    if server in SERVERS:
        subprocess.call(["cs2-server", f"@{server}", "restart"])
        flash(f"Restarted server {server}")
    return redirect(url_for("index"))

@app.route("/getmatch/<match>")
def get_match(match: str):
    matches = os.listdir("matches")
    if match in matches:
        with open(f"matches/{match}") as f:
            data = f.read()
            data = json.loads(data)
            return jsonify(data)
    return {}


@app.route("/load/<server>")
def load_match(server: str):
    match = request.args.get("match")
    matches = os.listdir("matches")
    if server in SERVERS and match in matches:
        subprocess.call(["cs2-server", f"@{server}", "exec", "matchzy_loadmatch_url", f'\\"http://localhost:{PORT}/getmatch/{match}\\"'])
        flash(f"Loaded match {match} on server {server}")
    return redirect(url_for("index"))

@app.route("/matches")
def matches():
    with open("teams.txt") as f:
        teams = eval(f.read())
    return render_template("match_setup.html", maps=MAPS.keys(), servers=SERVERS, teams=teams)

@app.route("/creatematch")
def create_match():
    '''
    For bo1, team1 is CT and team2 is T
    For bo3:
        Map 1: team1 is CT, team2 is T
        Map 2: team1 is T, team2 is CT
        Map 3: knife determines
    '''
    with open("teams.txt") as f:
        teams = eval(f.read())
    team1 = request.args.get("team1")
    team2 = request.args.get("team2")
    bo = int(request.args.get("bo"))
    map1 = request.args.get("map1")
    map2 = request.args.get("map2")
    map3 = request.args.get("map3")
    match_id = round(time.time() * 1000)

    match_data = {
        "matchid" : match_id,
        "team1" : {
            "name" : team1,
            "players" : teams[team1]
        },
        "team2" : {
            "name" : team2,
            "players" : teams[team2]
        },
        "num_maps" : bo
    }

    if bo == 1:
        match_data["maplist"] = [map1]
        match_data["map_sides"] = ["team1_ct"]
    elif bo == 3:
        match_data["maplist"] = [map1, map2, map3]
        match_data["map_sides"] = ["team1_ct", "team2_ct", "knife"]
    
    match_name = f"{team1}_{team2}_bo{bo}_{match_id}.json"
    with open(f"matches/{match_name}", "w+") as f:
        match_data_json = json.dumps(match_data, indent=4)
        f.write(match_data_json)
    
    flash(f"Created match {match_name}")
    return redirect(url_for("index"))

@app.route("/teams")
def teams():
    with open("teams.txt") as f:
        teams = eval(f.read())
    return render_template("teams.html", teams=teams)

@app.route("/update_team/<team>", methods=["POST"])
def update_team(team):
    with open("teams.txt", "r+") as f:
        teams = eval(f.read())
        teams[team] = {
            request.form.get("id1") : request.form.get("name1"),
            request.form.get("id2") : request.form.get("name2")
        }
        f.seek(0)
        f.truncate()
        teams = json.dumps(teams, indent=4)
        f.write(teams)
        flash(f"Updated {team}")
    return redirect(url_for("index"))

@app.route("/add_team", methods=["POST"])
def add_team():
    with open("teams.txt", "r+") as f:
        teams = eval(f.read())
        team = request.form.get("team_name")
        teams[team] = {
            request.form.get("id1") : request.form.get("name1"),
            request.form.get("id2") : request.form.get("name2")
        }
        f.seek(0)
        f.truncate()
        teams = json.dumps(teams, indent=4)
        f.write(teams)
        flash(f"Added {team}")
    return redirect(url_for("index"))

async def changemap(server:str, map: str):
    await asyncio.sleep(2)
    subprocess.call(["cs2-server", f"@{server}", "exec", "host_workshop_map", f"{MAPS[map]}"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
