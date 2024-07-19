# utility script to build docker image
echo "Build and deploy bambuctl_publisher image..."

# check for 3 parameters
if [ $# -ne 3 ]; then
  echo "Usage: $0 <port> <redis_host> <redis_port>"
  exit 1
fi

# clear out any previous versions
docker stop bambuctl_publisher
docker rm bambuctl_publisher

# move dockerfile into place
cp Dockerfile ../src
cd ../src

# build and run docker image on port passed into script
docker image build -t bambuctl_publisher .
docker run --name bambuctl_publisher -d -p $1:51295 -e REDIS_HOST=$2 -e REDIS_PORT=$3 bambuctl_publisher

#cleanup
rm Dockerfile

# dump out running containers
echo "Running containers after deployment:"
docker ps

echo "Done."