import os
from spector.build_graph import build_graph


os.environ["OPENAI_API_KEY"] = "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"
os.environ['TAVILY_API_KEY'] = "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"

inputs = {"question": "阿卡利的技能是什麼？"}
config = {"configurable": {"thread_id": "abc123"}}
graph = build_graph()


for output in graph.stream(inputs, config):
    print("\n")

# Final generation
if 'rag_generate' in output.keys():
    print(output['rag_generate']['generation'])
elif 'plain_answer' in output.keys():
    print(output['plain_answer']['generation'])