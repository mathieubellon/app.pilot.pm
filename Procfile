web: sh -c 'cd ./back/ && daphne pilot.asgi:application --port=$PORT --bind 0.0.0.0'
rq_worker: python -u ./back/run_rq_worker.py
