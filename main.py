from datetime import datetime, timedelta
import os
import pathlib
import time
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status, Path, Query, Request, File, UploadFile
from sqlalchemy import text
from sqlalchemy.orm import Session

from connect import get_db
from middleware import CustomHeaderMiddleware
from models import User, Contact
from schemas import UserModel, UserResponse, ContactModel, ContactResponse

app = FastAPI()
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    logger.exception("Error handling request")
    return ...


# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     response.headers["X-Process-Time"] = str(process_time)
#     return response
#
#
# app.add_middleware(CustomHeaderMiddleware)


@app.get("/")
def read_root():
    return {"message": "Applicontaction started"}


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


@app.get("/users", response_model=List[UserResponse], tags=["users"])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@app.get("/users/{user_id}", response_model=UserResponse, tags=["users"])
async def get_user(user_id: int = Path(ge=0), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return user


@app.post("/users", response_model=UserResponse, tags=["users"])
async def create_user(body: UserModel, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=body.email, phone=body.phone).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is existing!",
        )
    user = User(name=body.name, surname=body.surname, phone=body.phone, email=body.email)
    db.add(user)
    db.commit()
    return user


@app.put("/users/{user_id}", response_model=UserResponse, tags=["users"])
async def update_user(body: UserModel, user_id: int = Path(gt=0), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    print(body.name, body.surname, body.phone, body.email)
    user.name = body.name
    user.surname = body.surname
    user.phone = body.phone
    user.email = body.email
    db.commit()
    return user


@app.delete("/users/{user_id}", response_model=UserResponse, tags=["users"])
async def delete_user(user_id: int = Path(ge=1), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    db.delete(user)
    db.commit()
    return user


@app.get("/contacts", response_model=List[ContactResponse], tags=["contacts"])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0, le=200),
                   db: Session = Depends(get_db)):
    contacts = db.query(Contact).limit(limit).offset(offset).all()
    return contacts


@app.get("/contacts/{contact_id}", response_model=ContactResponse, tags=["contacts"])
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return contact


@app.post("/contacts", response_model=ContactResponse, tags=["contacts"])
async def create_contact(body: ContactModel, db: Session = Depends(get_db)):
    contact = Contact(**body.model_dump())
    db.add(contact)
    db.commit()
    return contact


@app.put("/contacts/{contact_id}", response_model=ContactResponse, tags=["contacts"])
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    contact.name = body.name
    contact.surname = body.surname
    contact.birthday = body.birthday
    contact.description = body.description
    contact.phone = body.phone
    contact.email = body.email
    contact.user_id = body.user_id
    db.commit()
    return contact


@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["contacts"])
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    db.delete(contact)
    db.commit()
    return contact


@app.get("/contacts/search/{user_id}", response_model=ContactResponse, tags=["contacts"])
async def search_contact(
    user_id: int,
    contact_name: str = Query('Anon', min_length=2),
    surname: str = Query(None, min_length=2),
    email: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Contact).filter_by(user_id=user_id)
    if contact_name:
        query = query.filter_by(name=contact_name)
    if surname:
        query = query.filter_by(surname=surname)
    if email:
        query = query.filter_by(email=email)

    contact = query.first()

    if contact is None:
        raise HTTPException(
            status_code=404,
            detail="NOT FOUND",
        )
    return contact



@app.get("/contacts/birthdays/{user_id}", response_model=List[ContactResponse], tags=["contacts"])
async def upcoming_birthdays(user_id: int, db: Session = Depends(get_db)):
    current_date = datetime.now().date()
    future_birthday = current_date + timedelta(days=7)
    contacts = db.query(Contact).filter_by(user_id=user_id).filter(Contact.birthday >= current_date, Contact.birthday <= future_birthday).all()

    if not contacts:
        raise HTTPException(
            status_code=404,
            detail="No upcoming birthdays found for the user.",
        )

    return contacts

# # @app.post("/uploadfile/")
# # async def create_upload_file(file: UploadFile = File()):
# #     pathlib.Path("uploads").mkdir(exist_ok=True)
# #     file_path = f"uploads/{file.filename}"
# #     with open(file_path, "wb") as f:
# #         f.write(await file.read())
# #     return {"file_path": file_path}
#
# MAX_FILE_SIZE = 1_000_000
#
#
# @app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile = File()):
#     pathlib.Path("uploads").mkdir(exist_ok=True)
#     file_path = f"uploads/{file.filename}"
#     file_size = 0
#     with open(file_path, "wb+") as f:
#         while True:
#             chunk = await file.read(1024)
#             if not chunk:
#                 break
#             file_size += len(chunk)
#             if file_size > MAX_FILE_SIZE:
#                 f.close()
#                 # os.unlink(file_path)
#                 pathlib.Path(file_path).unlink()
#                 raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
#                                     detail="File size is over the limit")
#             f.write(chunk)
#     return {"file_path": file_path}