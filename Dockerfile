FROM alpine:latest

RUN apk --update --upgrade add bash cairo pango gdk-pixbuf py3-cffi py3-pillow py-lxml
ADD ./app/requirements.txt ./
RUN pip3 install -r requirements.txt

RUN mkdir /myapp
WORKDIR /myapp
ADD ./app/server.py /myapp
RUN mkdir /root/.fonts
ADD ./.fonts/* /root/.fonts/

CMD gunicorn --bind 0.0.0.0:5001 server:app
