## Navodila za preizkus

Prvo

```
docker pull bluestern/mini-sistem-za-obracun-elektricne-energije
```

potem

```
docker network create mynetwork

```

potem

```
docker run -d --name db --network mynetwork -e POSTGRES_USER=devuser -e POSTGRES_PASSWORD=password -e POSTGRES_DB=devdb postgres:17-alpine

```

potem

```

docker run -it --rm -p 8000:8000 -e DATABASE_URL=postgresql://devuser:password@db:5432/devdb --network mynetwork bluestern/mini-sistem-za-obracun-elektricne-energije:latest

```

Po tej proceduri, bi moralo delati, ampak csv-ji ne bodo še naloženi.
Za naložiti (skrajšane) csv, container mora biti pognan v enem terminalu, v drugem terminalu pa se požene

```
docker exec -it <container_id> bash
```

Potem znotraj kontejnerja pa bi moralo bit na voljo za pognati:
`python import-csv-to-db.py --env dev`

## Ko je to narejeno, se v browserju na localhost port 8000 klikne na

- Upravljaj račune, narejeni bodo računi za stranke iz csv
- Upravljaj stranke, tam se strankam nastavi vsaj Ime in Priimek
- potem se gre na Ustvari račun, se najde željeno stranko
- in izbere, da se želi ustvariti račun

## Overview

This is a FastAPI backend for managing invoices (`računi`) linked to clients (`stranke`). It supports PDF generation via WeasyPrint and CSV import for bulk data ingestion. Built with SQLAlchemy, Alembic, and Docker for reproducible development and deployment.

1. Import csv, this will populate `fastapi_vhodni_podatki` table
2. Add a new stranka, stranka's id will be auto-generated
3. Create a new račun, conveniently, you can find the stranka you wish by searching

## Env files

- To use local postgres, rename env.dev.example to .env.dev
- To use live aiven postgres, you need .env.prod, which is not in the codebase

## Project structure

- `main.py` – FastAPI entry point
- `models/` – SQLAlchemy models
- `routers/` – API route definitions
- `alembic/` – Database migrations
- `import-csv-to-db.py` – CSV import script
- `docker-compose.dev.yml` – Development setup
- `docker-compose.prod.yml` – Production setup

## Running the app

### Without Docker

You may need to install dependencies first
.\venv\Scripts\activate
uvicorn.exe main:app --reload

### With Docker

#### Development

docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up

#### Production

docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up

## CSV import (new)

```

docker-compose up

```

and in another terminal

```

docker-compose exec fastapi python import-csv-to-db.py --env dev

```

it will generate some temporary fake stranka_id

## CSV import (old)

Currently you have to import the `.csv` files manually by running:

```

import-csv-to-db.py

```

It will "link" the CSV data with `stranka` based on the number in the `.csv` filename.

## Installing dependencies

- `apt-get` – System-level packages (OS, binaries), compilers, database clients, C libs
- `pip` – Python packages for your app (FastAPI, Alembic, SQLAlchemy, etc.)
- `pip freeze > requirements.txt` – May produce too many dependencies; use carefully

### Example

```

./venv/bin/pip install weasyprint

```

## Changes in table definitions

### Create a new migration

You need to run migrations with Alembic. Make sure you're inside the virtual environment:

```

./venv/bin/alembic revision --autogenerate -m "Add new table"

```

For the production live database, you may need to enter changes manually, e.g. with pgAdmin

### Apply migration

```

./venv/bin/alembic upgrade head

```

Make sure your models are imported in `alembic/env.py`.

## Testing

Not implemented.

## Deployment notes

- Production image is tagged as `fastapi-app:prod`
- Healthcheck endpoint: `/health`
- PDF generation uses WeasyPrint (requires system libraries)
- Database must support SSL (e.g. Aiven PostgreSQL)

# TODO

- Importing multiple times the same csv currently is not notifying the user
- DATABASE_URL many times cannot be read when running within docker

```

```

```

```
