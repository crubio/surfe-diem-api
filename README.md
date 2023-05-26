Local development:

# start venv
source venv/bin/activate

# Database 
start PostgreSQL server, app should create databases
- todo: create a seed migration script
- todo: relational tables
- update, create, delete should be admin only ops

# start the webserver
uvicorn app.main:app --reload

# login & jwt
- select which routes depend on a login token