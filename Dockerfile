FROM ubuntu:latest
MAINTAINER Amal Zohny "amaal.zohny@gmail.com"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]

# docker build -t flask-sample-one:latest .
# docker run -d -p 80:80  flask-sample-one
# docker ps -a
# docker stop d209be8327a2