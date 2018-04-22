## Dependencies
### Python3
```bash
brew update
brew install python3
```
#### flask, flask_cors, psycopg2
```bash
pip3 install flask
pip3 install flask_cors
pip3 install psycopg2
```
### Postgres
```bash
brew install postgres
```
<br />
## Run the server
### Start postgres
```bash
brew services start postgres
```
### Create databse
You need to create a database called `cammy`

```bash
psql postgres
create database cammy;
```

Create two tables to save user account and sent messages:

```bash
psql cammy
create table messages (
	name text,
	email text,
	phone_number text,
	subject text,
	message text
);

create table users (
	email text,
	password text
);
```

Then run the server:

```bash
python3 run_local.py
```