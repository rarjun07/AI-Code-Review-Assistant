from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/hello")
def say_hello():
    return {
        "message": "Hello Arjun"
    }

@app.get("/vehicle")
def get_vehicle():
    return {
        "id": 1,
        "name": "Honda City"
    }

@app.get("/student")
def get_Student():
    return{
        "Name":"Arjun Singh",
        "Class":"M.Sc",
        "Rollno:":"7773"
    }

@app.get("/student/{student_id}")
def get_student(student_id: int):
    return {
        "student_id": student_id
    }

@app.get("/vehicle/{vehicle_id}")
def get_vehicle(vehicle_id:int):
    return{
        "vehicle_id":vehicle_id
    }

@app.get("/booking/{booking_id}")
def get_booking(booking_id:int):
    return{
        "booking_id":booking_id
    }

@app.get("/vehicle/name/{vehicle_name}")
def get_vehicle(vehicle_name:str):
    return{
        "vehicle_name":vehicle_name
    }



@app.get("/search")
def search(name: str):
    return {
        "searched_name": name
    }

# @app.post("/student")
# def create_student():
#     return {
#         "message": "Student Created"
#     }


# from fastapi import FastAPI

# app = FastAPI()

# @app.post("/student")
# def create_student(
#     name: str
# ):
#     return {
#         "student_name": name
#     }

# class Student(BaseModel):
#     name: str
#     course: str


from fastapi import FastAPI
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI()

# Create Schema
class Student(BaseModel):
    name: str
    course: str

# Create Endpoint
@app.post("/student")
def create_student(student: Student):
    return {
        "name": student.name,
        "course": student.course
    }