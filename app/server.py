#!/usr/bin/env python
import os
import json
import logging

from flask import Flask, request, make_response
import weasyprint
from weasyprint import HTML
import boto3

BUCKET = os.environ.get('AWS_BUCKET')
KEY = os.environ.get('AWS_BUCKET_KEY')

app = Flask('pdf')

@app.route('/health')
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
    filename = request.form.get('filename', 'unnamed.pdf')
    app.logger.info('POST  /pdf?filename=%s' % filename)

    url = request.form.get('url')
    app.logger.info('POST  /pdf?url=%s' % url)

    s3_client = boto3.client('s3')
    s3_client.download_file(BUCKET, url, '/tmp/testes.html')

    html = HTML('/tmp/testes.html')
    html.write_pdf('/tmp/%s' % filename)

    response = s3_client.upload_file('/tmp/%s' % filename, BUCKET, 'export-pdf/%s' % filename, ExtraArgs={'ACL': 'public-read', 'ContentType': 'application/pdf' })
    file_url = '%s/%s/%s' % (s3_client.meta.endpoint_url, BUCKET, 'export-pdf/%s' % filename)
    app.logger.info(file_url)

    response = make_response(file_url)
    response.headers['Content-Type'] = 'application/text'
    # response.headers['Content-Disposition'] = 'inline;filename=%s' % filename
    app.logger.info(' ==> POST  /pdf?filename=%s  ok' % filename)

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
