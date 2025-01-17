# for run:
uvicorn app.main:app --reload

# for run with docker:
docker compose up --build || docker compose up

# for migrations
alembic revision --autogenerate -m "Initial migrations"
alembic upgrade head

# for tests:
pytest tests/test_post.py