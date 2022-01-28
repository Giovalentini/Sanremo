# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /APP

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies, then remove requirements file
RUN pip install -r requirements.txt \
    && pip install 'jupyterlab == 3.0.7' \
    && rm requirements.txt 

# copy the content of the local src directory to the working directory
COPY src/ .

# Spin up a jupyter lab
CMD jupyter lab --ip 0.0.0.0 --port 8888 --no-browser --allow-root