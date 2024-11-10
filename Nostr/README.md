# Chatbot Nostr Client

## Introduction

This chatbot Nostr Client is retrofit the python client (https://github.com/jeffthibault/python-nostr)

The schematic drawing in https://excalidraw.com/#room=8c49ec331c267f1c311a,YrEycYr2G93zrf7gdfTkjQ 

## Docker-compose setup
`docker-compose build` to setup the docker image. Each time you change the code, you need to run this command again.
`docker-compose up` to run the docker image. 

### postgres dashboard
Once the docker image is running, you can access the pgdamin app at `http://localhost:5050`. 
The log in information can be found in the `docker-compose.yml` file.
- Email: ${PGADMIN_EMAIL}
- Password: ${PGADMIN_PASSWORD}

Tutorial: https://youtu.be/NH4VZaP3_9s?t=708

## Local Installation
Recommend to create a new anaconda environment. [guide](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)
Then inside the conda environment, run `pip install -r requirements` to install the packages.

### Setup postgres
WSL or linux environment:
```
sudo apt update
```
install postgres
```
sudo apt install postgresql postgresql-contrib
```
 start service
 ```
 sudo service postgresql start
 ```
Then setup the DB Env. 
For example:

`DATABASE=chat_record`

`DBUSER=bot_dbuser`

`PASSWORD=9527`

change user
```
sudo -i -u postgres
psql

```
create db,user and password
```
CREATE USER bot_dbuser WITH PASSWORD '9527';
CREATE DATABASE chat_record;
GRANT ALL PRIVILEGES ON DATABASE chat_record TO bot_dbuser;
``` 

## Usage

**Register a nostr account on web app**

https://snort.social/global

After registration, you will get:
- two public keys: one starts with `npub` will be used to put in the `.env` file.
- one private key: starts with `nsec`, this will be put in the `.env` file too.

**ChatBase bot**

https://www.chatbase.co/

- Put the chatbase `API_KEY` into the `.env` file.
- Each chatbot has its own `BOT_ID`, input it into the `.env` file.

**Run the bot client**

`python app.py`