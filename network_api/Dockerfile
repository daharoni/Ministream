FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements/base.txt
RUN pip install -r network_api/requirements.txt

ENV PYTHONPATH=/app

CMD ["uvicorn", "network_api.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
