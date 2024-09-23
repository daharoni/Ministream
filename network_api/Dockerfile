FROM python:3.8-slim

WORKDIR /app

COPY requirements /app/requirements
RUN pip install -r requirements/base.txt
RUN pip install -r network_api/requirements.txt

COPY . .

CMD ["uvicorn", "network_api.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
