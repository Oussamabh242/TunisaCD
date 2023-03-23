from fastapi import FastAPI 
from Users import users

app = FastAPI()
app.include_router(router = users.router)


@app.get("/")
def home() : 
    return {"msg" : "sfs"} 