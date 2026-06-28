FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY compiler ./compiler
COPY runtime ./runtime
COPY operators ./operators
COPY planner ./planner

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "runtime.api:app", "--host", "0.0.0.0", "--port", "8000"]
