# convenience to run the app
echo loading environment variables
source .env

echo running migrations
python migrate.py

echo starting application
NUM_CORES=$(nproc)
echo NUM_CORES $NUM_CORES
NUM_WORKERS=$(expr 2 \* $NUM_CORES + 1)
echo NUM_WORKERS $NUM_WORKERS
gunicorn -b $IVOLAPI_HOST:$IVOLAPI_PORT -w $NUM_WORKERS -k uvicorn.workers.UvicornWorker app:app
