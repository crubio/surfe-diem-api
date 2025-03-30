# WIP surf & weather forecasting data API

# how to run locally
First clone this repo by using following command
````

git clone https://github.com/crubio/surfe-diem-api.git

````
then 
````

cd surfe-diem-api

````

Then install requirements

````

pip3 install -r requirements.txt

````

Then go this repo folder in your local computer run follwoing command
````

uvicorn main:app --reload

````
or you can try this command if the previous one is throwing errors

````

uvicorn app.main:app --host=127.0.0.1 --port=${PORT:-5000}

````

Then you can use following link for documentation about the API

````
http://127.0.0.1:8000/api/v1

````

## Setting up postgres
If you want to use postgres, the code is still in the repo. Add these to your envars file.
Create a database in postgres then create a file name .env and write the following things in your file 

````
DATABASE_HOSTNAME = localhost
DATABASE_PORT = 5432
DATABASE_PASSWORD = passward_that_you_set
DATABASE_NAME = name_of_database
DATABASE_USERNAME = User_name
SECRET_KEY = 1234567890
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 60(base)

````

## Setting up SQLite
Create a file name .env and write the following things in your file 

````
SECRET_KEY = 1234567890
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 60(base)
DATABASE_URL=sqlite:///./surfe-diem-api.db
DATABASE_URI=sqlite:///./surfe-diem-api.db
SQLITE_URI=sqlite:///./surfe-diem-api.db
SQLITE_DB=./surfe-diem-api.db
ENVIRONMENT=development

````

## Seeding the database
Run the following command in the root of the project to seed the database with some data
````
jobs/run_db_setup.sh
````

You can also use docker to do this if you prefer to run postgres in a container with `docker-compose -f docker-compose.yml up`. Use `psql` to create the database specified in .env

### Note: SECRET_KEY in this exmple is just a psudo key. You need to get a key for youself and you can get the SECRET_KEY  from fastapi documantion 