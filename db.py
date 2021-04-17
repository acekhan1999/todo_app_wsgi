from pymongo import MongoClient
from bson.objectid import ObjectId

cluster = MongoClient("mongodb+srv://to_do_app:to_do_app123@cluster0.h3kct.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["todo_app"]
users_collection = db["users"]
todo_collection = db["todo"]

def insert_user(userObj):
    users_collection.insert_one(userObj)
    print("user inserted in db")

def insert_todo(todoObj):
    todo_collection.insert_one(todoObj)
    print("todo inserted in db")

def get_todos(userID):
    user_todo_db = todo_collection.find({"userID":userID})
    user_todo = []

    for todo in user_todo_db:
        user_todo.append(todo)

    return user_todo

def get_user_todo(todoID):
    todo = todo_collection.find_one({"_id" : ObjectId(todoID)})
    return todo

def get_user(username, password):
    user = users_collection.find_one({"username": username, "password": password})
    return user

def remove_todo(todo_id):
    todo_collection.delete_one({"_id": ObjectId(todo_id)})

def update_todo(todo_id):
    todo_collection.update_one({"_id": ObjectId(todo_id)}, {"$set" : {"completed" : True}})