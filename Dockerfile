FROM debian:latest

RUN apt-get update && apt-get install -y sudo apt-utils pip python3 sqlite3

RUN apt-get install python3-bs4 python3-requests python3-discord python3-cairosvg python3-dotenv -y

COPY ./src /app

WORKDIR /app

CMD ["/usr/bin/python3", "/app/bot.py"]