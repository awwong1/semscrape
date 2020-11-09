# semscrape

MuckRack take home assignment. Create a Django web application to scrape a web publication, perform article sentiment analysis, and enable users to search (main keyword association, products) scraped articles and view sentiment/relevant heuristics.

[Example Usage](https://swift-yeg.cloud.cybera.ca:8080/v1/AUTH_e3b719b87453492086f32f5a66c427cf/media/2020/11/08/muck_rack_takehome_example.gif)

## Quickstart

To quickly run a development version of the application:

```bash
docker-compose build
docker-compose run web python manage.py migrate
docker-compose run web python manage.py collectstatic
docker-compose up

# In new terminal
# To rebuild the elastic search indices
docker-compose run web python manage.py search_index --rebuild # enter y at prompt
# To immediately trigger an RSSFeed crawl (otherwise occurs every 30 mins)
docker-compose run web python manage.py fetchrssnow
# To create a superuser for the admin site
docker-compose run web python manage.py createsuperuser

```

A development version of the site should now be available at `localhost:8000`.

### Developer Setup

Manual setup of persistence volumes, use Python virtual environment.

```bash
# setup venv
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt

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

# elasticsearch image
docker pull elasticsearch:7.9.3
mkdir -p ${HOME}/docker/volumes/elasticsearch_data
docker run \
  --rm \
  --name elasticsearch \
  --env "discovery.type=single-node" \
  --publish 9200:9200 \
  --publish 9300:9300 \
  --volume ${HOME}/docker/volumes/elasticsearch_data:/usr/share/elasticsearch/data \
  --detach \
  elasticsearch:7.9.3

# celery worker (not detached)
celery -A semscrape worker --beat --loglevel=INFO
```
#### Search API Endpoint

A Django Rest Framework API for searching ElasticSearch is available at
`/search/articles/`.
Some example API calls:
- `/search/articles/?limit=10&search=tesla&format=json`
    - Return first 10 articles containing 'tesla', ensure JSON returned
- `/search/articles/?limit=10&offset=20&ordering=-publication_date`
    - Return 10 articles (offset by 20 articles) ordered by descending publication date
- `/search/articles/4412e95a-abca-4014-aef2-879fdcf58d50/`
    - Return a single article

#### Testing

```bash
# only unit tests
python3 manage.py test

# For coverage
coverage run --source="." --omit=venv/* manage.py test
coverage html
firefox htmlcov/index.html
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
