# Install base dependencies
FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get clean && rm -rf /var/lib/apt
RUN apt-get -y update && apt-get -y install python3.8 python3-pip libgl1-mesa-dev ffmpeg libsm6 libxext6 libgl1-mesa-glx python3-opencv

# Add working directory
ADD src /src
WORKDIR /src

# Install main dependencies
RUN pip3 install -r requirements.txt

# Run command
EXPOSE 8080
CMD ["waitress-serve", "--port", "8080", "app:app"]
