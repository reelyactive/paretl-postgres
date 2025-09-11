# Run as a package
python -m src.main -c config/config.json


# Set up the dev env
conda create -n myenv python=3.12
conda activate myenv
conda install numpy pandas plotly matplotlib nbformat

# Build and run the docker
sudo docker build -t etl_app .
sudo docker images
https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images

# Make the postgresql listen to the docker, add the following lines
sudo nano /etc/postgresql/16/main/postgresql.conf 
listen_addresses = '*'
sudo nano /etc/postgresql/16/main/pg_hba.conf 
host all all 172.17.0.0/16 md5
sudo systemctl restart postgresql


sudo docker run \
  --add-host=host.docker.internal:host-gateway \
  -v $(pwd)/config:/app/config \
  etl_app python -m src.main -c config/config.json

   
# Install docker
sudo snap install docker  


