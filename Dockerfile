# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install git and nano for convenience inside the container
RUN apt-get update && apt-get install -y git nano

# Command to keep the container running if needed,
# but we will primarily use `docker exec` to get a shell.
CMD ["tail", "-f", "/dev/null"]
