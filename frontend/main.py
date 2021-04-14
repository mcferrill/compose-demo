#!/usr/bin/env python

from flask import Flask, render_template, redirect, request
from minio import Minio
from werkzeug.utils import secure_filename
import boto3
import os
try:
    from livereload import Server
except ImportError:
    Server = None

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/uploads'


@app.route('/')
def index():
    init()
    return render_template('index.html', files=get_bucket().objects.all())


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' in request.files:
        f = request.files['file']
        filename = os.path.join(app.config['UPLOAD_FOLDER'],
                                secure_filename(f.filename))
        f.save(filename)
        get_bucket().put_object(Body=open(filename, 'rb').read(),
                                Key=f.filename)
        os.remove(filename)
    return redirect('/')


# API

def init():
    """Use minio API to set up bucket and sample file."""

    client = Minio('minio:9000',
                   access_key='minioadmin',
                   secret_key='minioadmin',
                   secure=False)
    if not client.bucket_exists('files'):
        client.make_bucket('files')
    if 'sample.c10' not in client.list_objects('files'):
        client.fput_object('files', 'sample.c10', 'sample.c10')


def get_bucket():
    init()
    s3 = boto3.resource('s3',
                        endpoint_url='http://minio:9000',
                        aws_access_key_id='minioadmin',
                        aws_secret_access_key='minioadmin')
    return s3.Bucket('files')


@app.route('/api/v1/resources/files/all', methods=['GET'])
def list_files():
    return [o.key for o in get_bucket().objects.all()]


if __name__ == '__main__':
    if Server is not None:
        app.jinja_env.auto_reload = True
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        server = Server(app.wsgi_app)
        server.serve()
