# Set up the dev env
conda create -n myenv python=3.12
conda activate myenv
conda install numpy pandas plotly matplotlib nbformat

# Build and run the docker
docker build -t etl_app .
docker run --rm --network="host" -v $(pwd)/config.json:/app/config.json etl_app
