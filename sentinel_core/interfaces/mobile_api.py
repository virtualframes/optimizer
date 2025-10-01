from fastapi import FastAPI
from agents.sentinel import SentinelAgent

app = FastAPI()
agent = SentinelAgent()

@app.post("/signal")
def receive_signal(signal: dict):
    agent.monitor(signal)
    return {"status": "processed"}