# convenience to run the app
source .env
uvicorn app:app --port $FASTAPI_PORT --host $FASTAPI_HOST --reload
