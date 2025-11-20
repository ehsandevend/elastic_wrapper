# ElasticSearch Wrapper

use below syntax to build docker compose:
    sudo docker compose --env-file ./.app_envs/docker/.env  -f docker-compose-dev.yml build
    sudo docker compose --env-file ./.app_envs/docker/.env  -f docker-compose-dev.yml up -d
    sudo docker compose --env-file ./.app_envs/docker/.env  -f docker-compose-dev.yml down
    sudo docker logs -f --tail 10 elastic_wrapper-elastic-wrapper-app-1