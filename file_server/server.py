import os
from flask import Flask, request, jsonify, Response
import logging
from flask_sslify import SSLify
import ssl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Flask(__name__)
# context = ('/ssl/cert.pem', '/ssl/key.pem')
# sslify = SSLify(app, permanent=True, ssl_context=context)
context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain('/ssl/cert.pem', '/ssl/key.pem')
sslify = SSLify(app, permanent=True, ssl_context=context)

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


if __name__ == "__main__":
    app.run(
		host='0.0.0.0',
		debug=False,
		# port=int(os.environ.get("PORT", 80))
		port=int(os.environ.get("PORT", 443))
		)
