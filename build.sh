cp docker/Dockerfile .

IMAGE_NAME="fast-api-nexus2"
IMAGE_TAG="latest"

docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

echo "The image is created"

rm Dockerfile
