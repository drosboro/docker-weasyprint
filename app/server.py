#!/usr/bin/env python
import os
import json
import logging

from flask import Flask, request, make_response
import weasyprint
from weasyprint import HTML
import boto3

BUCKET_ORIGIN = os.environ.get('AWS_ORIGIN_BUCKET')
BUCKET_ORIGIN_KEY = os.environ.get('AWS_ORIGIN_BUCKET_KEY')
BUCKET_DESTINATION = os.environ.get('AWS_DESTINATION_BUCKET')
BUCKET_DESTINATION_KEY = os.environ.get('AWS_DESTINATION_BUCKET_KEY')

app = Flask('pdf')

@app.route('/status')
def index():
    return 'ok'

@app.route('/version')
def version_index():
    return weasyprint.__version__


@app.before_first_request
def setup_logging():
    logging.addLevelName(logging.DEBUG, "\033[1;36m%s\033[1;0m" % logging.getLevelName(logging.DEBUG))
    logging.addLevelName(logging.INFO, "\033[1;32m%s\033[1;0m" % logging.getLevelName(logging.INFO))
    logging.addLevelName(logging.WARNING, "\033[1;33m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
    logging.addLevelName(logging.ERROR, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR))

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)


@app.route('/')
def home():
    return '''
        <h1>PDF Generator</h1>
        <p>The following endpoints are available:</p>
        <ul>
            <li>POST to <code>/pdf?filename=myfile.pdf</code>. The body should
                contain html</li>
            <li>POST to <code>/multiple?filename=myfile.pdf</code>. The body
                should contain a JSON list of html strings. They will each
                be rendered and combined into a single pdf</li>
        </ul>
    '''

@app.route('/pdf', methods=['POST'])
def generate():
    name = request.args.get('filename', 'unnamed.pdf')
    app.logger.info('POST  /pdf?filename=%s' % name)
    html = HTML(string=request.data)
    pdf = html.write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline;filename=%s' % name
    app.logger.info(' ==> POST  /pdf?filename=%s  ok' % name)


@app.route('/pdfS3', methods=['POST'])
def generateFromS3():
    origin_filename = request.form.get('originFilename', 'unnamed.pdf')
    destination_filename = request.form.get('destinationFilename', 'unnamed.pdf')
    app.logger.info('POST  /pdfS3?originFilename=%s' % origin_filename)
    app.logger.info('POST  /pdfS3?destinationFilename=%s' % destination_filename)

    origin_path = '/tmp/%s' % origin_filename
    origin_object_name = '%s/%s' % (BUCKET_ORIGIN_KEY, origin_filename)
    app.logger.info('POST  /pdfS3?origin_object_name=%s' % origin_object_name)
    destination_path = '/tmp/%s' % destination_filename
    destination_object_name = '%s/%s' % (BUCKET_DESTINATION_KEY, destination_filename)
    app.logger.info('POST  /pdfS3?destination_object_name=%s' % destination_object_name)

    s3_client = boto3.client('s3')
    s3_client.download_file(BUCKET_ORIGIN, origin_object_name, origin_path)

    html = HTML(origin_path)
    html.write_pdf(destination_path)

    response = s3_client.upload_file(
        destination_path,
        BUCKET_DESTINATION,
        destination_object_name,
        ExtraArgs={ 'ACL': 'public-read', 'ContentType': 'application/pdf' }
    )
    
    file_url = '%s/%s/%s' % (s3_client.meta.endpoint_url, BUCKET_DESTINATION, destination_object_name)
    app.logger.info(file_url)

    response = make_response(file_url)
    response.headers['Content-Type'] = 'application/text'
    # response.headers['Content-Disposition'] = 'inline;filename=%s' % filename
    app.logger.info(' ==> POST  /pdfS3?filename=%s  ok' % destination_object_name)

    return response


@app.route('/multiple', methods=['POST'])
def multiple():
    name = request.args.get('filename', 'unnamed.pdf')
    app.logger.info('POST  /multiple?filename=%s' % name)
    htmls = json.loads(request.data.decode('utf-8'))
    documents = [HTML(string=html).render() for html in htmls]
    pdf = documents[0].copy([page for doc in documents for page in doc.pages]).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline;filename=%s' % name
    app.logger.info(' ==> POST  /multiple?filename=%s  ok' % name)
    return response


if __name__ == '__main__':
    app.run()
