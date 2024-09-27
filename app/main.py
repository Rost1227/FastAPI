from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional, List
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy import *
from sqlalchemy.orm import Session
from .database  import engine, get_db
from . import models, schemas
from .database import db_name, db_host, db_password, db_username, engine, SessionLocal

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


my_posts = [{"title": "title post 1", "content": "content of post  1", "id": 1}, {"title": "favourit foods", "content": "i like pizza", "id": 2}]

@app.get("/")

def root():

    return {"message": "Welcome to my api bro"}

# get posts using raw sql
# @app.get("/posts")
# def get_posts():
#     cursor.execute("""SELECT * FROM posts """)
#     posts = cursor.fetchall()
#     return posts

# get posts using ORM

@app.get("/posts", response_model = list[schemas.Post])
def get_posts( db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

# create post using  raw SQL
# @app.post("/posts", status_code=status.HTTP_201_CREATED)
# def create_post(post: schemas.PostCreate):
#     cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
#     new_post = cursor.fetchone()
#     conn.commit()
#     return new_post

# create post using ORM
@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# get post by id using raw sql
# @app.get("/posts/{id}")
# def get_post(id: int):
#     cursor.execute("""SELECT * from posts WHERE id = %s """, (str(id)))
#     post = cursor.fetchone()

#     if not post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with id {id} not found")
#     return post

# get post by id using ORM
@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with id {id} not found")
    return post

# delete post by id using raw sql
# @app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_post(id: int):
#     cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
#     deleted_post = cursor.fetchone()
#     if deleted_post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with id {id} not found")
#     conn.commit()
#     return Response(status_code= status.HTTP_204_NO_CONTENT)

# delete post by id using ORM
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    if post_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with id {id} not found")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code= status.HTTP_204_NO_CONTENT)

# update post by id using raw sql
# @app.put("/posts/{id}")
# def update_post(id: int, post: schemas.PostCreate):
#     cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
#     updated_post = cursor.fetchone()
#     if updated_post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with id {id} not found")

#     conn.commit()

#     return updated_post

# update post by id using ORM
@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with id {id} not found")
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()
