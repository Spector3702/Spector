import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from spector.lib.build_graph import build_graph

graph = build_graph()
app = FastAPI()

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
    if 'rag_generate' in output.keys():
        generation = output['rag_generate']['generation']
    elif 'plain_answer' in output.keys():
        generation = output['plain_answer']['generation']

    return {"generation": generation}


if __name__ == "__main__":
    uvicorn.run("spector.main:app", host="0.0.0.0", port=5000, proxy_headers=True)