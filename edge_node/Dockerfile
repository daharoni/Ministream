FROM nvcr.io/nvidia/l4t-base:r32.6.1

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-bad1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    libglib2.0-dev \
    libgirepository1.0-dev \
    libcairo2-dev

WORKDIR /app

COPY requirements /app/requirements
COPY edge_node/requirements.txt /app/edge_node/requirements.txt 

RUN pip3 install -r requirements/base.txt
RUN pip3 install -r edge_node/requirements.txt

COPY . .

CMD ["python3", "edge_node/src/main.py"]
