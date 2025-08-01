from flask import Flask, render_template, redirect, request, url_for, flash
import subprocess
import asyncio

app = Flask(__name__)
app.secret_key = 'suck my fat hairy sweaty balls, por favor'

MAPS = {
    "de_foroglio" : "3132854332",
    "de_lake" : "3219506727",
    "de_palais" : "3257582863",
    "de_eldorado" : "3408790618",
    "de_dogtown": "3414036782",
    "de_neptune" : "3430103877",
    "de_splat" : "3439120481"
}

SERVERS = {
    "game1" : "48.221.120.18:27015",
    "game2" : "48.221.120.18:27017",
    "game3" : "48.221.120.18:27019",
    "game4" : "48.221.120.18:27021"
}

@app.route("/")
def index():
    return render_template("index.html", maps=MAPS.keys(), servers=SERVERS)

@app.route("/start/<server>")
def start(server: str):
    map = request.args.get("map")
    if map and map in MAPS:
        subprocess.call(["cs2-server", f"@{server}", "start"])
        loop = asyncio.get_event_loop()
        loop.create_task(changemap(server, map))
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

async def changemap(server:str, map: str):
    await asyncio.sleep(20)
    subprocess.call(["cs2-server", f"@{server}", "exec", "host_workshop_map", f"{MAPS[map]}"])

if __name__ == "__main__":
    app.run(host="0.0.0.0")
