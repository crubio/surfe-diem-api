# surfe-diem API

A surf and weather forecasting data API built with FastAPI.

## 🚀 Overview

surfe-diem provides surf spot, buoy, tide, and weather data via a modern REST API. Designed for surf forecasting apps, dashboards, and enthusiasts.

## 📁 Project Structure

- `app/` - Main application code (models, routers, classes, etc.)
- `tests/` - Unit and integration tests
- `jobs/` - Shell scripts for setup and maintenance
- `data/` - Static data files (JSON, etc.)
- `tools/` - Utility scripts

## 🏁 Quickstart

### 1. Clone the repo
```bash
git clone https://github.com/crubio/surfe-diem-api.git
cd surfe-diem-api
```

### 2. Install dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Set up your `.env` file
(see Environment Variables section below for details)

### 4. Run the API
```bash
uvicorn app.main:app --reload
```

### 5. API Docs
Visit [http://127.0.0.1:8000/api/v1](http://127.0.0.1:8000/api/v1) for interactive docs.

## ⚙️ Environment Variables

| Variable                     | Description                        | Example                        |
|------------------------------|------------------------------------|--------------------------------|
| DATABASE_HOSTNAME            | Postgres host                      | localhost                      |
| DATABASE_PORT                | Postgres port                      | 5432                           |
| DATABASE_PASSWORD            | Postgres password                   | yourpassword                   |
| DATABASE_NAME                | Postgres DB name                    | surfe_diem_api                 |
| DATABASE_USERNAME            | Postgres user                       | postgres                       |
| SECRET_KEY                   | JWT secret key                      | (generate your own)            |
| ALGORITHM                    | JWT algorithm                       | HS256                          |
| ACCESS_TOKEN_EXPIRE_MINUTES  | JWT expiry in minutes               | 60                             |
| SQLITE_URI                   | SQLite DB URI                       | sqlite:///./surfe-diem-api.db  |
| DATABASE_URL                 | Alternative DB URL                  | postgresql://user:pass@host/db |
| DATABASE_URI                 | Alternative DB URI                  | postgresql://user:pass@host/db |
| SQLITE_DB                    | SQLite database file path           | ./surfe-diem-api.db            |
| ENVIRONMENT                  | Environment name                    | development                    |

## 🗄️ Database Setup

### PostgreSQL
Create a database in PostgreSQL, then create a `.env` file with:
```bash
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_PASSWORD=password_that_you_set
DATABASE_NAME=name_of_database
DATABASE_USERNAME=User_name
SECRET_KEY=1234567890
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### SQLite (Recommended for Development)
Create a `.env` file with:
```bash
SECRET_KEY=1234567890
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./surfe-diem-api.db
DATABASE_URI=sqlite:///./surfe-diem-api.db
SQLITE_URI=sqlite:///./surfe-diem-api.db
SQLITE_DB=./surfe-diem-api.db
ENVIRONMENT=development
```

## 🌱 Seeding the Database
Run the following command in the root of the project to seed the database with some data:
```bash
jobs/run_db_setup.sh
```

## 🐳 Docker
To run with Docker:
```bash
docker-compose up
```

You can also use Docker to run PostgreSQL in a container with `docker-compose -f docker-compose.yml up`. Use `psql` to create the database specified in your `.env` file.

## 🧪 Testing

This project uses [pytest](https://docs.pytest.org/) for unit and integration testing.

### Test Dependencies
- pytest
- httpx
- pytest-asyncio
- fastapi
- pandas
- python-jose
- passlib
- bcrypt
- email-validator
- python-multipart
- geopy

Install all dependencies with:
```bash
pip3 install -r requirements.txt
```
Or, for just the test dependencies:
```bash
pip3 install pytest httpx pytest-asyncio fastapi pandas python-jose passlib bcrypt email-validator python-multipart geopy
```

### Test Structure
- All tests are in the `tests/` directory.
- Unit tests for classes and methods are in `tests/test_basic.py`.
- Integration tests for API endpoints are in `tests/test_integration.py`.

### Running Tests
To run all tests:
```bash
python3 -m pytest -v
```
To run a specific test file:
```bash
python3 -m pytest tests/test_integration.py -v
```

### Writing New Tests
- Add new test files in the `tests/` directory.
- Use `pytest` fixtures for shared setup.
- Use FastAPI's `TestClient` for endpoint tests.

### Example: Root Endpoint Integration Test
```python
from fastapi.testclient import TestClient
from app.main import app

def test_root_endpoint():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "hello from surfe-diem"}
```

## 🛠️ Development

### Common Commands
- **Migrations:** `alembic upgrade head`
- **Linting:** `flake8 app/`
- **Formatting:** `black app/`
- **Run with reload:** `uvicorn app.main:app --reload`
- **Run on specific port:** `uvicorn app.main:app --host=127.0.0.1 --port=${PORT:-5000}`

### Code Style
- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings to functions and classes

## 🤝 Contributing

Open an issue or pull request! All contributions are welcome.

### Before Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 🐞 Troubleshooting

### Common Issues

**Dependency errors:**
```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

**Database connection issues:**
- Check your `.env` file configuration
- Ensure your database server is running
- Verify database credentials

**Port already in use:**
```bash
uvicorn app.main:app --port=8001
```

**Import errors:**
- Make sure all dependencies are installed
- Check Python version compatibility (Python 3.8+)

### Getting Help
- Check the [FastAPI documentation](https://fastapi.tiangolo.com/)
- Review existing issues in the repository
- Open a new issue with detailed error information

## 📝 Notes

- The SECRET_KEY in examples is just a pseudo key. You need to generate your own secure key. You can get guidance on generating a SECRET_KEY from the [FastAPI documentation](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/).

## 📬 Contact

For questions, open an issue or contact the maintainer.

---

Happy coding! 🏄‍♂️ 