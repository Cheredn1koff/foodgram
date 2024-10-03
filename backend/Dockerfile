FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY foodgram/ .

CMD ["/bin/bash", "./start_server.sh"]
#CMD ["gunicorn", "--bind", "0.0.0.0:9000", "foodgram.wsgi"]