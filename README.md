*******************
# This is the archive repository of the pilot.pm Saas.
After 10 years of an incredible lifetime adventure we must put down our company.
I couldn't just delete this code, build by many, over so much time.
So here it is, publicly accessible.
Farewell my old friend, you did brilliantly.
*******************


The pilot backend runs on python v3.7+, the frontend is written in ES6 javascript, transpiled with babel and bundled with webpack.

# Install the development server

Pilot will need :
 - Python 3.7+ : django backend
 - Node.js 12+ : frontend bundling + subprocess calls from python
 - PostgreSQL 9.6+ : database
 - Redis 5+ : job queue, realtime server channel layer ( not yet for cache )
 - ElasticSearch : search
 
You can run the dev server without ElasticSearch ( search won't work ) and Redis ( job queue and realtime won't work ).

It's recommended to setup a python virtualenv :

```
python3 -m venv pilot_env
source pilot_env/bin/activate
```

Then you can install the python dependencies with pip ( which should be installed by default in your venv) :

```
pip install -r back/requirements/dev.txt
```

Install the frontend dependencies ( this will create the node_modules directory ) :

```
cd front && yarn
```

Finally you'll need to set some environment variable to run the backend server correctly.
A list of the variables you can define is available in the file `pilot/settings/.env.example`
We recommend the usage of the direnv tool : just copy `pilot/settings/.env.example` into the root path and rename it `.env`.

You'll need at least the `DATABASE_URL` and `SECRET_KEY` variables to start the server.

#### OSX

You need to `export LDFLAGS="-L/usr/local/opt/openssl/lib"` before running pip3 install for psycopg2 to build correctly


# Running the development server

You need to launch two local servers : webpack-dev-server for the frontend assets ( with hot reload ) and django's runserver for the backend.
There are two fabric commands for a quick launch :

```
fab watch
```
and
```
fab devserver
```

# Running the job queue

To run the job queue, you'll need an active Redis server and PostgreSQL server.

To start the workers and begin consuming the job queue :

```
python run_rq_worker.py
```

The job queue is required for those features :
 
 - All data exports
 - Project Copy
 - ItemType update
 - Mention update
 - SavedFilter notification
 - Search vector update

# Run all services with Docker app

Install docker desktop on your machine
https://www.docker.com/products/docker-desktop

## Build project
In project folder this command will build all services and run them (output attached to console, else use -d option to launch as daemon process). 
```
docker-compose up
```
In other terminal
```
docker-compose run --rm web python manage.py migrate
docker-compose run --rm web python manage.py load_demo_data
```


## Running project : 

In project folder this command will start all services in order.
```
docker-compose up
```
Application will be available at http://127.0.0.1:8000

## Debug orchestration tips

If you need to build just one container
```
docker build -t apppilotpm_web .
```

Launch service only with service deps and remove afterwards (if you need to debug something in this service alone)
```
docker-compose run --rm --service-ports web
```

Rebuild service without launching deps
```
docker-compose up --no-deps --build web
```
