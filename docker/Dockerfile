# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /app

# Create log mount point
RUN mkdir /app/log

# Copy the current directory contents into the container at /app
COPY . /app

# Install lftp and any needed packages specified in requirements.txt
RUN apt-get update && \
    apt-get install -y lftp && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install -r requirements.txt

# Make port 51295 available to the world outside this container
EXPOSE 51295

# Run app when the container launches
CMD ["python3", "app.py"]