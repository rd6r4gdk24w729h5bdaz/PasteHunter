# Using Docker
* Install Docker & docker-compose
* cd /opt
* git clone ....
* cd PasteHunter
* chmod -R 777 data
* mv settings.json.sample settings.json
* docker build . -t pastehunter-core
* mv neo4j-docker-compose.yml docker-compose.yml
* docker-compose up -d
