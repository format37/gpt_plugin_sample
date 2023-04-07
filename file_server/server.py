import os
from flask import Flask, request, jsonify, Response, render_template, send_file
from flask_cors import CORS
import logging
import ssl
import json
import requests
import urllib.parse
import requests
from bs4 import BeautifulSoup
import json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://chat.openai.com"}})
# HOST_URL = "https://langtea.club"
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


@app.route("/request", methods=["GET"])
def get_request():
	query = request.args.get("url")
	body = web_to_json(query)
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
		text = text.replace("langtea.club", f"https://{host}")
		return Response(text, mimetype="text/json")


@app.route("/openapi.yaml", methods=["GET"])
def openapi_spec():
	host = request.headers['Host']
	with open("openapi.yaml") as f:
		text = f.read()
		# This is a trick we do to populate the PLUGIN_HOSTNAME constant in the OpenAPI spec
		text = text.replace("langtea.club", f"https://{host}")
		return Response(text, mimetype="text/yaml")
	

def web_to_json(url, max_tokens = 1000):
	logger.info(f"Requesting URL: {url}")
	response = requests.get(url)
	logger.info(f"Response status code: {response.status_code}")

	soup = BeautifulSoup(response.text, 'html.parser')

	# Remove images and styles from the webpage
	for img in soup.find_all('img'):
		img.extract()

	for style in soup.find_all('style'):
		style.extract()

	# Extract links from webpage
	links = []
	for link in soup.find_all('a'):
		link_data = {
			'href': link.get('href'),
			'text': link.text.strip()
		}
		links.append(link_data)

	# Extract text content from webpage
	text = soup.get_text()
	text = text.replace('\n', '')
	text = text.replace('\r', '')
	text = text.replace('\t', '')
	text = text.replace('\xa0', '')

	text_length = len(text)
	# split by spaces
	text_tokens = text.split(' ')
	logger.info(f"Text length: {text_length}")
	if len(text_tokens) > max_tokens:
		text = text[:max_tokens]
		text = text + '...'
		links = links[:1]
		logger.info(f"Text length after truncation: {len(text)}")
		logger.info(f"Text words count after truncation: {len(text.split(' '))}")
		logger.info(f"Links length after truncation: {len(links)}")

	# Convert text content and links into JSON structure
	json_data = {
		'url': url,
		'text': text,
		'links': links
	}
	return json_data


if __name__ == "__main__":
	app.run(
		host='0.0.0.0',
		debug=False,
		port=int(os.environ.get("PORT", 443)),
		ssl_context=context
		)
