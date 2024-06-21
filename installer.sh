#!/bin/bash

apt-get update && apt-get install -y sudo apt-utils pip python3 sqlite3

apt-get install python3-bs4 python3-requests python3-discord python3-cairosvg python3-dotenv -y

sqlite3 src/db/database.sqlite < src/db/create_db.sql
