from typing import Collection
from model import BloodSugar, MyExerciseData
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from fastapi import HTTPException 

print(datetime.date(datetime.now()))
client = AsyncIOMotorClient('mongodb+srv://dbUser:chula123@cluster0.nds32.mongodb.net/myFirstDatabase?ssl=true&ssl_cert_reqs=CERT_NONE')

# database = client.bright
# collection = database.bloodsugar

async def fetch_all_bloodsugar(username):
    db = client[username]
    collection = db.bloodsugar
    bloodsugar = []
    cursor = collection.find({})
    async for document in cursor:
        bloodsugar.append(BloodSugar(**document))
    return bloodsugar

async def create_bloodsugar(bloodsugar, username):
    db = client[username]
    collection = db.bloodsugar
    bloodsugar_check = []
    cursor = collection.find({})
    async for document in cursor:
        bloodsugar_check.append(BloodSugar(**document))
    data_in_a_day = 0
    for a in bloodsugar_check:
        if a.date == str(datetime.date(datetime.now())):
            data_in_a_day = data_in_a_day + 1
    # print("data_in_a_day", data_in_a_day)
    if data_in_a_day < 8:
        print("data_in_a_day", data_in_a_day)
        document = bloodsugar
        result = await collection.insert_one(document)
        return document
    else:
        raise HTTPException(400, 'You cannot put more today')


async def update_bloodsugar(username, mealtype, date, time, bloodlevel):
    db = client[username]
    collection = db.bloodsugar
    document = await collection.update_one({"mealtype": mealtype, "date":date},
                                {"$set": {"bloodsugar": bloodlevel, "time": time}})
    return {"res", "Updated Successfully"}
    # document = bloodsugar

    # for data in 
    # result = await collection.insert_one(document)
    # return document

# async def update_bloodsugar(bloodsugar, username):
#     db = client[username]
#     collection = db.bloodsugar
#     document = bloodsugar
#     result = await collection.insert_one(document)
#     return document

########### Exercise ################
async def create_myexercise(MyExerciseData, username):
    db = client[username]
    collection = db.exercise
    document = MyExerciseData
    result = await collection.insert_one(document)
    return document

async def fetch_all_myexercise(username):
    db = client[username]
    collection = db.exercise
    myexercise = []
    cursor = collection.find({})
    async for document in cursor:
        myexercise.append(MyExerciseData(**document))
    return myexercise

async def update_Myexercise(username, minute, intensity, date):
    db = client[username]
    collection = db.exercise
    document = await collection.update_one({"date":date},
                                    {"$set": {"minute":minute, "intensity": intensity}}
    )
    print("document", document)
    # # exercise = await collection.update_one(
    # #     {"exercise": exercise, "date": date},
    # #     {"$set": {"done":done}}
    # # )
    # # result = await collection.update_one
    # print(document)
    return document

#################################
