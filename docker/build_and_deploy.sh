# utility script to build docker image
echo "Build and deploy bambuctl_publisher image..."

# clear out any previous versions
docker stop bambuctl_publisher
docker rm bambuctl_publisher

#set $1 to default port if not passed in
if [ -z "$1" ]
  then
    echo "No port argument supplied, using default port 51295"
    set -- "51295"
fi

# move dockerfile into place
cp Dockerfile ../src
cd ../src

# build and run docker image on port passed into script
docker image build -t bambuctl .
docker run --name bambuctl_publisher -d -v bambuctl_publisher:/app/log -p $1:51295 bambuctl_publisher

#cleanup
rm Dockerfile

# dump out running containers
echo "Running containers after deployment:"
docker ps

echo "Done."