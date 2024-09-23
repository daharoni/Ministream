FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    python3-pyqt6 \
    libgl1-mesa-glx

WORKDIR /app

COPY requirements /app/requirements
RUN pip install -r requirements/base.txt
RUN pip install -r gui/requirements.txt

COPY . .

CMD ["python", "gui/src/main.py"]
