FROM python:3.10

RUN apt-get update && apt-get install -y python3-dev supervisor nginx && rm -rf /var/lib/apt/lists/*

COPY requirements/prod_requirements.txt /twitter_clone/
RUN pip install -r /twitter_clone/prod_requirements.txt

COPY app/ /twitter_clone/app/
COPY nginx.conf /etc/nginx/nginx.conf
COPY ./static /usr/share/nginx/html
COPY supervisord.ini /etc/supervisor/conf.d/supervisord.ini

WORKDIR /twitter_clone/app/
ENV PYTHONPATH="/twitter_clone:${PYTHONPATH}"

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.ini"]