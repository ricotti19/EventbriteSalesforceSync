from fastapi import FastAPI, Request # type: ignore

app = FastAPI()

@app.post("/webhook")
async def handle_eventbrite_webhook(request: Request):
    # catches the raw JSON package sent down the ngrok tunnel
    payload = await request.json()
    print("EVENTBRITE WEBHOOK CAUGHT")
    print(payload)
    
    return {"status": "success", "message": "Payload received"}

if __name__ == "__main__":
    import uvicorn # type: ignore
    # runs the server on port 8000, exactly where ngrok is pointing
    uvicorn.run(app, host="0.0.0.0", port=8000)