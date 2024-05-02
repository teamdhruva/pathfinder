from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/status")
async def status():
    return Response(status_code=204)

@app.get("/picture")
async def picture():
    return Response(status_code=501)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
