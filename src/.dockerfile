FROM python:3.8-slim-buster

WORKDIR /app/src

COPY ./             /app/src


EXPOSE 8001
CMD [ "python3", "server.py"]

