import uvicorn
from fastapi import FastAPI, Response
from pydantic import BaseModel
from psycopg_pool import ConnectionPool

from spector.lib.build_graph import build_graph
from spector.app.healthz_middleware import HealthzMiddleware


connection_pool = ConnectionPool(
    conninfo=(
        f"postgresql://postgres:spector3702@my-release-postgresql.spector.svc.cluster.local:5432/spector?sslmode=disable"
    ),
    max_size=20,
    kwargs={
        "autocommit": True,
        "prepare_threshold": 0,
    },
)
graph = build_graph(connection_pool)
app = FastAPI()
app.add_middleware(HealthzMiddleware, connection_pool=connection_pool)


class ChatModel(BaseModel):
    question: str
    thread_id: str


@app.post("/chat")
def chat_endpoint(data: ChatModel):
    inputs = {"question": data.question}
    config = {"configurable": {"thread_id": data.thread_id}}

    for output in graph.stream(inputs, config):
        print("\n")

    generation = None
    if "rag_generate" in output.keys():
        generation = output["rag_generate"]["generation"]
    elif "plain_answer" in output.keys():
        generation = output["plain_answer"]["generation"]

    return {"generation": generation}


@app.get("/health/liveness")
def liveness_probe():
    return Response(status_code=200)

@app.get("/health/readiness")
def readiness_probe():
    try:
        connection_pool.check()
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=503)

@app.get("/health/metrics")
def prometheus_metrics():
    # 这里可以返回应用程序的指标数据
    return Response(content="your_prometheus_metrics", media_type="text/plain")


def main():
    uvicorn.run("spector.app.main:app", host="0.0.0.0", port=5000, proxy_headers=True)


if __name__ == "__main__":
    main()
