from collections import namedtuple
from typing import Optional, Dict
from fastapi import FastAPI, HTTPException, Depends, Request,status, File, UploadFile
from fastapi.responses import JSONResponse,ORJSONResponse
from pydantic import BaseModel
from hashing import Hash
from jwttoken import create_access_token
from oauth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import json as js
from database import (
    fetch_all_bloodsugar,
    create_bloodsugar,
    create_myexercise,
    fetch_all_myexercise,
    update_Myexercise,
    update_bloodsugar
)
from model import BloodSugar, MyExerciseData, UpdateMyExerciseData

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "https://main.d2l0l61pk96pbn.amplifyapp.com/:443",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


mongodb_uri = 'mongodb+srv://dbUser:chula123@cluster0.nds32.mongodb.net/myFirstDatabase?ssl=true&ssl_cert_reqs=CERT_NONE'
port = 8000
client = MongoClient(mongodb_uri, port)
db = client["User"]

class User(BaseModel):
    username: str
    real_name: Optional[str] = None
    surname: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    weight: Optional[int] = None
    height: Optional[int] = None
    tel: Optional[str] = None
    email: Optional[str] = None
    password: str
    confirmpassword: Optional[str] = None

class Login(BaseModel):
	username: str
	password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    username: Optional[str] = None

@app.get("/", response_model=User)
def read_root(current_user:User = Depends(get_current_user)):
    response =  db["users"].find_one({'username':current_user.username})
    return response

@app.post('/register')
def create_user(request:User):
    hashed_pass = Hash.bcrypt(request.password)
    user_object = dict(request)
    user_object["password"] = hashed_pass
    a = db["users"].find_one({'username':user_object['username']})
    if(a):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f'User already exist with this {user_object["username"]} username')
    else:
        user_id = db["users"].insert(user_object)
        return JSONResponse(status_code=status.HTTP_201_CREATED)
 
@app.post('/login')
def login(request:OAuth2PasswordRequestForm = Depends()):
	user = db["users"].find_one({"username":request.username})
	if not user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f'No user found with this {request.username} username')
	if not Hash.verify(user["password"],request.password):
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f'Wrong Username or password')
	access_token = create_access_token(data={"sub": user["username"] })
	return {"access_token": access_token, "token_type": "bearer", "username": request.username}

#### Blood sugar ######
@app.post('/api/create_bloodsugar/{username}', response_model=BloodSugar)
async def post_bloodsugar(bloodsugar: BloodSugar, username: str):
    bloodobject = dict(bloodsugar)
    db = client[username]
    collection = db.bloodsugar
    b = collection.find_one({"mealtype": bloodobject['mealtype'], "date":bloodobject['date']})
    if (b):
        print(bloodobject)
        update_response = await update_bloodsugar(username, bloodobject['mealtype'], bloodobject['date'], bloodobject['time'], bloodobject['bloodsugar'])
    else:
        response = await create_bloodsugar(bloodsugar.dict(), username)
        if response:
            return response
        else:
            raise HTTPException(400, 'Something went wrong / Bad Request')

@app.get('/api/get_bloodsugar/{username}')
async def get_bloodsugar(username):
    response = await fetch_all_bloodsugar(username)
    return response
#########################

#### my exercise #####
@app.post('/api/create_myexercise/{username}', response_model=MyExerciseData)
async def post_myexercise(myexercise: MyExerciseData, username: str):
    exercise_object = dict(myexercise)
    db = client[username]
    collection = db.exercise
    c = collection.find_one({ "date":exercise_object['date']})
    if (c):
        exercise_update = await update_Myexercise(username, exercise_object['minute'], exercise_object['date'])
    else:
        response = await create_myexercise(myexercise.dict(), username)
        if response:
            return response
        else:
            raise HTTPException(400, 'Something went wrong / Bad Request')

@app.get('/api/get_myexercise/{username}')
async def get_myexercise(username):
    response = await fetch_all_myexercise(username)
    return response

@app.put('/api/update_myexercise/{username}/{exercise}/{date}/{done}')
async def update_myexercise(username: str, exercise: str, date: str, done: bool):
    response = await update_Myexercise(username,exercise, date, done)
    return response
########################