FROM python:3.9

WORKDIR /app

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "app.py"]
