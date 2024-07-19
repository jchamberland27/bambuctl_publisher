# utility script to build docker image
echo "Build and deploy bambuctl_publisher image..."

# check for 3 parameters
if [ $# -ne 1 ]; then
  echo "Usage: $0 <port>"
  exit 1
fi

# clear out any previous versions
docker stop bambuctl_publisher
docker rm bambuctl_publisher

# move dockerfile into place
cp docker_env ../src
cp Dockerfile ../src
cd ../src

#WATTBOXIP=192.168.0.113
#WATTBOXUSER=admin

# build and run docker image on port passed into script
docker image build -t bambuctl_publisher .
docker run --name bambuctl_publisher -d -p $1:51295 --env-file docker_env bambuctl_publisher

#cleanup
rm Dockerfile
rm docker_env

# dump out running containers
echo "Running containers after deployment:"
docker ps

echo "Done."