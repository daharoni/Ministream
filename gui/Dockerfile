FROM python:3.8-slim

# Update package lists and install required dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    python3-tk \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxinerama1 \
    libxi6 \
    libxrandr2 \
    libxcursor1 \
    libxtst6 \
    libxss1 \
    libqt5x11extras5 \
    libxcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    libxkbcommon-x11-0 \
    libxcb-cursor0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements /app/requirements
COPY gui/requirements.txt /app/gui/requirements.txt
COPY shared /app/shared

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements/base.txt && \
    pip install --no-cache-dir -r gui/requirements.txt

COPY . .

ENV PYTHONPATH=/app:$PYTHONPATH
ENV QT_DEBUG_PLUGINS=1

CMD ["python", "gui/src/main.py"]
