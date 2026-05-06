FROM python:3.12-slim

WORKDIR /api

COPY ./apps/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./apps/api ./api
COPY ./apps/data/hockeyplayoffdb/hockeyplayoff.db ./data/hockeyplayoffdb/hockeyplayoff.db
ENV PYTHONPATH=/api
ENV DOCKER_ENV=true
EXPOSE 8000
CMD ["uvicorn", "api.hockeyplayoffapi.main:app", "--host", "0.0.0.0", "--port", "8000"]
