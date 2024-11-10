@echo off

COPY  "docker\Dockerfile" "."
SET IMAGE_NAME=fast-api-nexus2
SET IMAGE_TAG=latest
docker "build" "-t" "%IMAGE_NAME%:%IMAGE_TAG%" "."
DEL  "Dockerfile"