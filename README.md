# semscrape

MuckRack take home assignment. Create a Django web application to scrape a web publication, perform article sentiment analysis, and enable users to search (main keyword association, products) scraped articles and view sentiment/relevant heuristics.

## Quickstart

To quickly run a development version of the application:

```bash
docker-compose build
docker-compose up
```

### Developer Setup

Manual setup of persistence volumes.

```bash
# postgres image
docker pull postgres:13.0-alpine
mkdir -p ${HOME}/docker/volumes/postgres_data
docker run \
  --rm \
  --name postgresdb \
  --env POSTGRES_DB=semscrape-db \
  --env POSTGRES_USER=postgres \
  --env POSTGRES_PASSWORD=postgres \
  --publish 5432:5432 \
  --volume ${HOME}/docker/volumes/postgres_data:/var/lib/postgresql/data \
  --detach \
  postgres:13.0-alpine

# redis image
docker pull redis:6.0.9-alpine3.12
mkdir -p ${HOME}/docker/volumes/redis_data ${HOME}/docker/volumes/redis_conf
docker run \
  --rm \
  --name redis \
  --env REDIS_REPLICATION_MODE=master \
  --publish 6379:6379 \
  --volume ${HOME}/docker/volumes/redis_data:/var/lib/redis \
  --volume ${HOME}/docker/volumes/redis_conf:/usr/local/etc/redis/redis.conf \
  --detach \
  redis:6.0.9-alpine3.12 \
  redis-server

# celery worker (not detached)
celery -A semscrape worker --loglevel=INFO
```

## License

[Apache v2.0](./LICENSE)
```text
Copyright 2020 Alexander Wong

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
