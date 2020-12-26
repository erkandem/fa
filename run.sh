# convenience to run the app
echo loading environment variables
source .env
#uvicorn app:app --port $IVOLAPI_PORT --host $IVOLAPI_HOST --reload

echo running migrations
python migrate.py

echo starting application
#NUM_CORES=$(nproc)
#echo NUM_CORES $NUM_CORES
#NUM_WORKERS=$(expr 2 \* $NUM_CORES + 1)
#echo $NUM_WORKERS $NUM_WORKERS


gunicorn -b $IVOLAPI_HOST:$IVOLAPI_PORT -w 2 -k uvicorn.workers.UvicornWorker app:app
