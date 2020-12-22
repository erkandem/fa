# convenience to run the app
source .env
uvicorn app:app --port $IVOLAPI_PORT --host $IVOLAPI_HOST --reload
