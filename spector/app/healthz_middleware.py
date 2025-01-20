from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from psycopg_pool import ConnectionPool
from prometheus_client import CollectorRegistry, Gauge, generate_latest
import requests


class HealthzMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, connection_pool: ConnectionPool):
        super().__init__(app)
        self.connection_pool = connection_pool
        self.prefix = '/health'

    async def dispatch(self, request: Request, call_next):
        if request.url.path == f"{self.prefix}/liveness":
            return Response(status_code=200)

        if request.url.path == f"{self.prefix}/readiness":
            try:
                self.connection_pool.check()
                return Response(status_code=200)
            except Exception as e:
                return Response(status_code=503)

        if request.url.path == f"{self.prefix}/metrics":
            registry = CollectorRegistry()
            openai_api_up = Gauge('openai_api_up', 'Check if OpenAI API is up', registry=registry)

            try:
                response = requests.get("https://api.openai.com/v1/engines")
                if response.status_code == 200:
                    openai_api_up.set(1)
                else:
                    openai_api_up.set(0)
            except requests.exceptions.RequestException:
                openai_api_up.set(0)

            return Response(generate_latest(registry), media_type="text/plain")

        return await call_next(request)
