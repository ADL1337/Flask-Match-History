from flask import Flask, render_template, request, redirect, url_for
from riot_api import RiotAPI, REGIONS

app = Flask(__name__)
#app.secret_key = "1337CR3W"

@app.route("/")
def index():
    return render_template("base.html")

@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "POST":
        name = request.form["name"]
        if not name:
            return render_template("error.html", error="Name not found")
        region = request.form["region"]
        return redirect(url_for("profile", name=name, region=region))
    elif request.method == "GET":
        return render_template("search.html", regions=REGIONS)

@app.route("/profile/<region>/<name>")
def profile(name, region):
    if region not in REGIONS:
        return render_template("error.html", error="Region not found")
    if RiotAPI.verify_api_key():
        summoner = RiotAPI.summoner(name, region)
        if summoner is not None:
            matches = RiotAPI.matchlist(summoner.puuid, region, count=10)
        else:
            return render_template("error.html", error="Summoner not found")
        if matches is not None:
            return render_template("profile.html", summoner=summoner, matches=matches)
        else:
            return render_template("error.html", error="An error has occured while searching matches")
    else:
        return render_template("error.html", error="An error has occurred while searching summoner")

if __name__ == "__main__":
    app.run(debug=True)