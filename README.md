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

pip install -r requirements.txt

````

Then go this repo folder in your local computer run follwoing command
````

uvicorn main:app --reload

````

Then you can use following link for documentation about the API

````

http://127.0.0.1:8000/docs 

````

## Setting up postgres
Create a database in postgres then create a file name .env and write the following things in your file 

````
DATABASE_HOSTNAME = localhost
DATABASE_PORT = 5432
DATABASE_PASSWORD = passward_that_you_set
DATABASE_NAME = name_of_database
DATABASE_USERNAME = User_name
SECRET_KEY = 09d25e094faa2556c818166b7a99f6f0f4c3b88e8d3e7
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 60(base)

````

You can also use docker to do this if you prefer to run postgres in a container with `docker-compose -f docker-compose.yml up`. Use `psql` to create the database specified in .env

### Note: SECRET_KEY in this exmple is just a psudo key. You need to get a key for youself and you can get the SECRET_KEY  from fastapi documantion 