FROM python:3.10.4-alpine3.16

COPY requirements.txt requirements.txt

RUN apk add --no-cache git && pip3 install --no-cache-dir -r requirements.txt

COPY /bot /bot

CMD [ "python3.10", "bot" ]