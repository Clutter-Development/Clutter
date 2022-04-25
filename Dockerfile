FROM python:3.10.2-alpine3.15

WORKDIR /bot

COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY /bot .

CMD [ "python3.10", "__main__.py" ]