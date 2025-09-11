# Run as a package
python -m src.main -c config/config.json


# Set up the dev env
conda create -n myenv python=3.12
conda activate myenv
conda install numpy pandas plotly matplotlib nbformat

# Install docker
sudo snap install docker  

# Build and run the docker
sudo docker build -t etl_app .
sudo docker images

sudo docker tag etl_app prudentxavier/paretl:latest
sudo docker login -u prudentxavier
sudo docker push prudentxavier/paretl:latest


# Remove all stopped containers
sudo docker container prune -f
# Then remove all untagged images
sudo docker rmi $(sudo docker images | awk '/<none>/ {print $3}')


docker.io/prudentxavier/paretl:latest
docker pull prudentxavier/paretl:latest

sudo docker run \
  --add-host=host.docker.internal:host-gateway \
  -v $(pwd)/config:/app/config \
  prudentxavier/paretl:latest python -m src.main -c config/config.json


# Make the postgresql listen to the docker, add the following lines
sudo nano /etc/postgresql/16/main/postgresql.conf 
listen_addresses = '*'
sudo nano /etc/postgresql/16/main/pg_hba.conf 
host all all 172.17.0.0/16 md5
sudo systemctl restart postgresql

# Run the docker
sudo docker run \
  --add-host=host.docker.internal:host-gateway \
  -v $(pwd)/config:/app/config \
  etl_app python -m src.main -c config/config.json

   


