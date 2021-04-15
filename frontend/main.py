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
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024


# Helper function for development to initialize our test bucket.
def init():
    client = Minio('minio:9000',
                   access_key='minioadmin',
                   secret_key='minioadmin',
                   secure=False)
    if not client.bucket_exists('files'):
        client.make_bucket('files')
    if 'sample.c10' not in client.list_objects('files'):
        client.fput_object('files', 'sample.c10', 'sample.c10')


@app.route('/')
def index():
    files = get_bucket().objects.all()
    return render_template('index.html', files=files)


@app.route('/upload')
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


def get_bucket():
    init()
    s3 = boto3.resource('s3',
                        endpoint_url='http://minio:9000',
                        aws_access_key_id='minioadmin',
                        aws_secret_access_key='minioadmin')
    return s3.Bucket('files')


if __name__ == '__main__':
    if Server is not None:
        app.jinja_env.auto_reload = True
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        server = Server(app.wsgi_app)
        server.serve()
