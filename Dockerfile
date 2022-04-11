FROM python:3.9.7-slim-buster

# Install apache utils for testing
RUN apt-get -y update
RUN apt-get -y install apache2-utils

# Install the dependencies
#COPY requirements.txt /tmp/requirements.txt
#RUN pip install -r /tmp/requirements.txt

WORKDIR /app
# Copy the current directory contents into the container at /app
ADD . /app

CMD ["python3", "httpd.py", "-w", "10", "-r", "."]