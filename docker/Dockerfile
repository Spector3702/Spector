FROM python:3.13

# COPY spector/ /app/spector/
COPY setup.py /app/setup.py
WORKDIR /app

RUN pip install --no-cache-dir .

ENV PYTHONPATH="/app:$PYTHONPATH"
