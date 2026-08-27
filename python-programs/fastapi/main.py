import fastapi

app = fastapi.FastAPI()

@app.get("/greet")
async def greet():
    return {"message": "Welcome to the FastAPI application!"}

@app.get("/greet/{name}")
async def greet(name: str):
    return {"message": f"Hello, {name}!"}