import glob
import hashlib
import json
import logging
import os
import urllib
from datetime import datetime
from hashlib import md5

import pika
from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ["FLASK_KEY"]
DEBUG = os.environ["FLASK_DEBUG"] 
credentials = pika.PlainCredentials(os.environ['RABBITMQ_DEFAULT_USER'], os.environ["RABBITMQ_DEFAULT_PASS"])
ALLOWED_EXTENSIONS = set(["pdf", "jpg"])
UPLOAD_FOLDER = '/data/jobs'


@app.before_first_request
def setup_logging():
    if not app.debug:
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def count_jobs(path):
    """Count number of directories in workdir
    """
    return len(glob.glob(path))


@app.route("/", methods=['GET'])
def hello():
    completed_jobs = count_jobs("/data/jobs/*")
    return render_template('index.html', completed_jobs=completed_jobs)


@app.route("/about/", methods=['GET'])
def about():
    return render_template('about.html')


@app.route("/process/", methods=['POST'])
def process():

    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file uploaded')
        return redirect("/")
    file = request.files['file']

    # if user does not select file, browser also
    # submit an empty part without filename
    if file and allowed_file(file.filename) and file.filename != '':

        filename = secure_filename(file.filename)
        app.logger.info(f"Filename: {filename}")

        # make job folder
        m = hashlib.md5()
        m.update(filename.encode("utf-8") + datetime.now().isoformat().encode("utf-8"))
        md5string=m.hexdigest()
        target_folder = os.path.join(UPLOAD_FOLDER, md5string)
        os.mkdir(target_folder)

        file.save(os.path.join(target_folder, filename))

        # make queue message
        jd = dict()
        jd["jobid"] = md5string
        jd["filename"] = filename
        message = json.dumps(jd)
        app.logger.info(f"Job data: {message}")

        # Add to queue
        connection = pika.BlockingConnection(pika.ConnectionParameters('mq', 5672, '/', credentials, heartbeat=600, blocked_connection_timeout=300))
        channel = connection.channel()
        channel.queue_declare(queue='pimmer', durable=True)
        channel.basic_publish(exchange='', routing_key='pimmer', body=message, properties=pika.BasicProperties(delivery_mode = 2,))
        connection.close()
        app.logger.info(f"Created mq message for job {md5string}")

        return render_template('thankyou.html', output_folder="/data/result/" + md5string)
            
    else:
        flash('Upload a PDF file containing images')
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=DEBUG, port=8000)
