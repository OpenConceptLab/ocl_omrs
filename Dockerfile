FROM python:2.7

RUN apt-get update && \
  apt-get install -y default-mysql-client && \
  pip install --upgrade pip && \
  pip install mysql.connector


COPY ./requirements.txt /app/
COPY ./start.sh /app/

WORKDIR /app

RUN pip install -r requirements.txt

CMD "./start.sh"