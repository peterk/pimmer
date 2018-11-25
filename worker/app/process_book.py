import time
import os
import glob
import json
import shutil
import re
import sys
from os.path import basename
import logging
import traceback
import pika
import ghostscript
import locale

UPLOAD_FOLDER = '/data/jobs'
RESULT_FOLDER = "/data/result"


def cleanup(jobid):
    """Remove intermediate files.
    """
    pass


def pdf_to_images(filepath, output_folder):
    """Split a PDF file and make images of the individual pages

    :filepath: Path to PDF file
    :returns: tuple with output_folder and resulting file count

    """

    first_page = "1"

    args = [
        "-dNOPAUSE", "-dBATCH", "-dJPEGQ=60", "-r200", 
        "-dFirstPage=" + first_page,
        "-sDEVICE=jpeg",
        "-sOutputFile=" + os.path.join(output_folder, "page_%03d.jpg"),
        filepath
    ]

    encoding = locale.getpreferredencoding()
    args = [a.encode(encoding) for a in args]

    try:
        logging.info(args)
        ghostscript.Ghostscript(*args)
        logging.info(f"PDF file split")
        return (output_folder, len(glob.glob(output_folder)))

    except Exception as ex:
        print(ex)       



def extract_images(image_folder, resultdir):
    """Extract images from book pages in image_folder.

    :image_folder: path to jpg files.
    :resultdir: path to folder wher detected images should go.
    """
    logging.info(f"Finding images in {image_folder}...")

    images = glob.glob(os.path.join(image_folder, "*.jpg"))

    for image in images:
        command = f"python /app/extract.py --save-json --output-directory {resultdir} {image}"
        logging.info(f"Running {command}")
        os.system(command)



def handle_job(message):
    """Start working on a job in the queue.
    """
    logging.info(f"Started working on {message}")

    try:
        jdata = json.loads(message)
        jobid = jdata["jobid"]
        filename = jdata["filename"]

        logging.info(f"Splitting PDF {jobid}/{filename}")
        
        pdfpath = os.path.join(UPLOAD_FOLDER, jobid, filename)
        image_folder_path = os.path.join(UPLOAD_FOLDER, jobid)
        pdf_to_images(pdfpath, image_folder_path)

        # Detect images and illustrations in pages
        logging.info(f"Detecting images {jobid}/{filename}")
        resultdir = os.path.join(RESULT_FOLDER, jobid)
        os.mkdir(resultdir)
        extract_images(image_folder_path, resultdir)
        logging.info(f"Job {jobid} done!")

    except Exception:
        logging.error("Handle job broke", exc_info=True)
        if jdata:
            jsontxt = json.dumps(jdata, indent=4, sort_keys=True)
        else:
            jsontxt = ""
        message = f"Data: {jsontxt}\n\n\nERROR:\n{traceback.format_exc()}"



def callback(ch, method, properties, body):
    """Work on job from message queue."""
    logging.info(f"In callback for {body}...")
    handle_job(body)
    ch.basic_ack(delivery_tag = method.delivery_tag)
    logging.info(f"Job done! Sent ack for {body}...")



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    logging.info("Starting worker...")
    logging.info(f"Creds {os.environ['RABBITMQ_DEFAULT_USER']}")
    credentials = pika.PlainCredentials(os.environ['RABBITMQ_DEFAULT_USER'], os.environ["RABBITMQ_DEFAULT_PASS"])
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='mq', port=5672, heartbeat_interval=600, blocked_connection_timeout=300, virtual_host='/', credentials=credentials, connection_attempts=20, retry_delay=4))
    channel = connection.channel()
    channel.queue_declare(queue='pimmer', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue='pimmer')
    logging.info("Started consuming queue...")
    channel.start_consuming()
