import os
from flask import Flask, request, jsonify, Response, render_template, send_file
from flask_cors import CORS
import logging
import ssl
import json
import requests
import urllib.parse



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://chat.openai.com"}})
HOST_URL = "https://langtea.club"
context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain('/ssl/cert.pem', '/ssl/key.pem')

def send_file(filename, **options):
	"""Opens a file and streams it as the response body.  This is similar to
	:func:`send_from_directory` but it can also stream files from outside the
	:attr:`root_path` of the application.

	:param filename: the filename of the file to stream.
	:param options: all the options that :func:`send_from_directory` takes.
	"""
	# We have to set the cache control headers here because send_from_directory
	# will not do it for us.  We also have to set the content length because
	# otherwise Werkzeug will try to do range requests which won't work with
	# the file descriptor we're passing in.
	file = open(filename, 'rb')
	file.seek(0, os.SEEK_END)
	file_length = file.tell()
	file.seek(0)
	rv = Response(
		file,
		200,
		mimetype=options.pop('mimetype', None),
		headers=options.pop('headers', None),
		direct_passthrough=options.pop('direct_passthrough', False),
	)
	rv.headers['Content-Length'] = file_length
	rv.headers['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
	rv.headers['Cache-Control'] = 'no-cache'
	return rv


def send_from_directory(directory, filename, **options):
	"""Send a file from a given directory with :func:`send_file`.

	:param directory: the name of the directory to look in.
	:param filename: the name of the file to send.
	:param options: all the options that :func:`send_file` takes.
	"""
	filename = os.path.join(directory, filename)
	return send_file(filename, **options)


@app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory('/files', filename)


@app.route('/legal')
def serve_legal():
    return render_template('legal.html')

# Primary page index.html
@app.route('/')
def serve_index():
	return render_template('index.html')

@app.route("/players", methods=["GET"])
def get_players():
    query = request.args.get("query")
    res = requests.get(
        f"{HOST_URL}/api/v1/players?search={query}&page=0&per_page=100")
    body = res.json()
    return jsonify(body)


@app.route("/teams", methods=["GET"])
def get_teams():
    res = requests.get(
        f"{HOST_URL}/api/v1/teams?page=0&per_page=100")
    body = res.json()
    return jsonify(body)


@app.route("/games", methods=["GET"])
def get_games():
    query_params = [("page", "0")]
    limit = request.args.get("limit")
    query_params.append(("per_page", limit or "100"))
    start_date = request.args.get("start_date")
    if start_date:
        query_params.append(("start_date", start_date))
    end_date = request.args.get("end_date")

    if end_date:
        query_params.append(("end_date", end_date))
    seasons = request.args.getlist("seasons")

    for season in seasons:
        query_params.append(("seasons[]", str(season)))
    team_ids = request.args.getlist("team_ids")

    for team_id in team_ids:
        query_params.append(("team_ids[]", str(team_id)))

    res = requests.get(
        f"{HOST_URL}/api/v1/games?{urllib.parse.urlencode(query_params)}")
    body = res.json()
    return jsonify(body)


@app.route("/stats", methods=["GET"])
def get_stats():
    query_params = [("page", "0")]
    limit = request.args.get("limit")
    query_params.append(("per_page", limit or "100"))
    start_date = request.args.get("start_date")
    if start_date:
        query_params.append(("start_date", start_date))
    end_date = request.args.get("end_date")

    if end_date:
        query_params.append(("end_date", end_date))
    player_ids = request.args.getlist("player_ids")

    for player_id in player_ids:
        query_params.append(("player_ids[]", str(player_id)))
    game_ids = request.args.getlist("game_ids")

    for game_id in game_ids:
        query_params.append(("game_ids[]", str(game_id)))
    res = requests.get(
        f"{HOST_URL}/api/v1/stats?{urllib.parse.urlencode(query_params)}")
    body = res.json()
    return jsonify(body)


@app.route("/season_averages", methods=["GET"])
def get_season_averages():
    query_params = []
    season = request.args.get("season")
    if season:
        query_params.append(("season", str(season)))
    player_ids = request.args.getlist("player_ids")

    for player_id in player_ids:
        query_params.append(("player_ids[]", str(player_id)))
    res = requests.get(
        f"{HOST_URL}/api/v1/season_averages?{urllib.parse.urlencode(query_params)}")
    body = res.json()
    return jsonify(body)


@app.route("/logo.png", methods=["GET"])
def plugin_logo():
    filename = 'logo.png'
    return send_file(filename, mimetype='image/png')

@app.route("/.well-known/ai-plugin.json", methods=["GET"])
def plugin_manifest():
    host = request.headers['Host']
    with open("ai-plugin.json") as f:
        text = f.read()
        # This is a trick we do to populate the PLUGIN_HOSTNAME constant in the manifest
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return Response(text, mimetype="text/json")


@app.route("/openapi.yaml", methods=["GET"])
def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        # This is a trick we do to populate the PLUGIN_HOSTNAME constant in the OpenAPI spec
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return Response(text, mimetype="text/yaml")


if __name__ == "__main__":
    app.run(
		host='0.0.0.0',
		debug=False,
		port=int(os.environ.get("PORT", 443)),
		ssl_context=context
		)
