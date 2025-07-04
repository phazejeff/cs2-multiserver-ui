from flask import Flask, render_template, redirect, request, url_for, flash
import subprocess

app = Flask(__name__)
app.secret_key = 'suck my fat hairy sweaty balls, por favor'

MAPS = [
    "de_foroglio",
    "de_lake",
    "de_palais",
    "de_eldorado",
    "de_dogtown",
    "de_neptune",
    "de_splat"
]

SERVERS = [
    "game1",
    "game2",
    "game3",
    "game4"
]

@app.route("/")
def index():
    return render_template("index.html", maps=MAPS, servers=SERVERS)

@app.route("/start/<server>")
def start(server: str):
    map = request.args.get("map")
    if map and map in MAPS:
        subprocess.call([f"MAP={map}", "cs2-server", f"@{server}", "start"])
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

if __name__ == "__main__":
    app.run()
