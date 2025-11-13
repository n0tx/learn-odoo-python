# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install system dependencies required for psycopg2, plus git and nano
RUN apt-get update && apt-get install -y build-essential libpq-dev git nano

# Install Python libraries
RUN pip install psycopg2-binary

# Command to keep the container running if needed,
# but we will primarily use `docker exec` to get a shell.
CMD ["tail", "-f", "/dev/null"]
