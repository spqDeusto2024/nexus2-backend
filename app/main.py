from fastapi import FastAPI
from typing import Union
from app.controllers.handler import Controllers
from app.mysql.mysql import DatabaseClient

import app.utils.vars as gb
import app.models.models as models


def initialize() -> None:
  # initialize database
  dbClient = DatabaseClient(gb.MYSQL_URL)
  dbClient.init_database()
  return


app = FastAPI()
controllers = Controllers()

initialize()


@app.get('/healthz')
async def healthz():
  return controllers.healthz()

@app.post('/user/create')
async def create_user(body: models.UserRequest):
  return controllers.create_user(body)

@app.post('/user/delete')
async def delete_user(body: models.DeleteRequest):
  return controllers.delete_user(body.id)
  
@app.get('/user/get_all')
async def get_all_users():
  return controllers.get_all()

@app.post('/user/update')
async def update_user(body: models.UpdateRequest):
  return controllers.update_user(body)

# @app.post('/user/create')
# def createUser():
