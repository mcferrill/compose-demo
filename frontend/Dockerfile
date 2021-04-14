FROM tiangolo/meinheld-gunicorn-flask:python3.8-alpine3.11
RUN pip install minio boto3
RUN mkdir /uploads
COPY . /app
