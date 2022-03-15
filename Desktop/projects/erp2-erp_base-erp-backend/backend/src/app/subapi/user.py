from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
import sys
from .. import crud, model, schema, jwtUtils, bcryptUtils
from ..crud import get_db
user_subapi = APIRouter()


@user_subapi.post("/login", status_code=200)
def checkUser(user: schema.UserCheck, db: Session = Depends(get_db)):
    db_user = crud.getUserByAccount(db, userAccount=user.account)
    if db_user is None or db_user==[]:
        raise HTTPException(status_code=400, detail="Account not exist")
    if not bcryptUtils.bcryptVerify(user.pwd, db_user.pwd):
        raise HTTPException(status_code=400, detail="Password not correct")
    role = ''
    if db_user.status == 0:
        role = 'common'
    elif db_user.status == 1:
        role = 'su'
    elif db_user.status == 2:
        role = 'admin'
    return {
        'access_token': jwtUtils.generateJwt(db_user.account, role),
        "token_type": "bearer",
        'status': db_user.status
    }
    # db_user = model.User(account=db_user.account, pwd=db_user.pwd, status=db_user.status)
    # raise HTTPException(status_code=500, detail="success")


@user_subapi.post("/", status_code=200)
def create_user(user: schema.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.getUserByAccount(db, userAccount=user.account)
    if db_user:
        raise HTTPException(status_code=400, detail="Account already registered")
    return crud.createUser(db=db, user=user)




#
# @user_subapi.put("/",status_code=200)
# def updateUser(request: Request, update_user: schema.UserUpdate, db: Session = Depends(get_db)):
#     token = ''
#     try:
#         token = request.headers['Authorization']
#     except KeyError:
#         pass
#
#     try:
#         token = request.headers['authorization']
#
#     except KeyError:
#         pass
#
#     user_account = jwtUtils.generateJwt(token)
#     update = crud.updateUser(db, user_account, update_user)
#     if update is None:
#         raise HTTPException(status_code=400, detail="User not found")
#     raise HTTPException(status_code=200, detail="success")


__all__ = ["user_subapi"]
