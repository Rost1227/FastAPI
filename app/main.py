from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from .database  import engine
from . import models
from .database import db_name, db_host, db_password, db_username, engine
from .routers import post, user, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


while True:
    try:
        conn = psycopg2.connect( host = db_host , dbname = db_name , user = db_username , password = db_password, cursor_factory =  RealDictCursor)
        cursor = conn.cursor()
        print("Database conncection was succesfull!")
        break
    except Exception as error:
        print("Connection to Databse failed!")
        print("Error:", error)
        time.sleep(2)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Welcome to my api bro"}