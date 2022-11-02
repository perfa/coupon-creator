FROM python:3.9

RUN groupadd -r billo && useradd -r -g billo billo

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY . /app
WORKDIR /app
RUN rm -fr tests
RUN rm -fr .git
RUN chown -R billo /app

USER billo
EXPOSE 5000
CMD ["gunicorn", "--log-config", "/app/gunicorn_logging.conf", "--conf", "/app/gunicorn_conf.py", "--bind", "0.0.0.0:5000", "-k", "egg:meinheld#gunicorn_worker", "--worker-class=gthread", "--timeout", "60", "app.application:app"]