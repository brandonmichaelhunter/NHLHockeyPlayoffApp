FROM python:3.12-slim

WORKDIR /api

COPY ./requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./api ./api
COPY ./data/hockeyplayoffdb/hockeyplayoff.db ./data/hockeyplayoffdb/hockeyplayoff.db

EXPOSE 8000
CMD ["uvicorn", "api.hockeyplayoffapi.main:app", "--host", "0.0.0.0", "--port", "8000"]
