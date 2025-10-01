import uvicorn
from .router import app

def main():
    uvicorn.run(app, host="0.0.0.0", port=int(8080))