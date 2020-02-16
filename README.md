# Bot
To start, you must install the PostgreSQL database.
Then you need to create table, this is necessary to store the history.  
You can do this with the following command:
~~~~sql
CREATE TABLE history(
    download_time TIMESTAMP PRIMARY KEY,
    content text
);
~~~~
The config.json file must specify the database and bot parameters.  
Fields Value:
* "database" - the database name (database is a deprecated alias)
* "user" - user name used to authenticate
* "host" - password used to authenticate
* "port" - database host address (defaults to UNIX socket if not provided)
* "password" - connection port number (defaults to 5432 if not provided)
* "token" - TelegramBot token

Also need to install dependencies for python.  
You can do this with the following command:
```console
pip3 install -r requirements.txt
```
To start the bot, you need to run the command:  
```console
python3 bot.py
```
