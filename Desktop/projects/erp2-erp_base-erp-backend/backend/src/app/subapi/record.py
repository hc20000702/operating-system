from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
import sys

from .. import crud, model, schema, jwtUtils, bcryptUtils
from sqlalchemy import func
from ..crud import get_db
recore_subapi = APIRouter()


@recore_subapi.get("/getRecordById/{id}")
def getRecordById(id: int, db: Session = Depends(get_db)):
    db_order=db.query(model.OrderRecord).filter(model.OrderRecord.id == id).first()
    if db_order==[] or db_order is None:
        return []
    good = crud.getGoodById(db, db_order.goodId)
    setattr(db_order, "goodName", good.name)
    return db_order


@recore_subapi.get("/getAllRecord/{page}")
def get_record(page: int, db: Session = Depends(crud.get_db)):
    count = db.query(func.count(model.OrderRecord.id)).scalar()

    skip = (page - 1) * 10
    limit =  10

    result = db.query(model.OrderRecord).offset(skip).limit(limit).all()
    for order in result:
        good = crud.getGoodById(db, order.goodId)
        setattr(order, "goodName", good.name)
    data={
        "count":count,
        "data":result
    }

    return data


@recore_subapi.post("/getRecordByTime")
def getRecordByTime(ordertime: schema.OrderTime, db: Session = Depends(crud.get_db)):
    if ordertime.start is None:
        raise HTTPException(status_code=400, detail="please give a start time ")
    if ordertime.end is None:
        utctime = datetime.utcnow()
        utctime = utctime.strftime("%Y-%m-%d %H:%M:%S")
        ordertime.end = utctime

    result = db.query(model.OrderRecord).filter(model.OrderRecord.time >= ordertime.start).filter(
        model.OrderRecord.time <= ordertime.end).order_by(model.OrderRecord.time.desc()).all()
    for order in result:
        good = crud.getGoodById(db, order.goodId)
        setattr(order, "goodName", good.name)
    return result


@recore_subapi.get("/getRecordByProvide/{provide}")
def getRecordByProvide(provide: str, db: Session = Depends(crud.get_db)):
    result = db.query(model.OrderRecord).filter(model.OrderRecord.provider_id == provide).all()
    for order in result:
        good = crud.getGoodById(db, order.goodId)
        setattr(order, "goodName", good.name)

    return result


@recore_subapi.post("/getRecordByOptions", status_code=200)
def getRecordByOptions(orderOption: schema.recordOption, db: Session = Depends(crud.get_db)):
    # goodName:str
    # orderId:int=0
    # start: str
    # end: str = None
    if orderOption.end is None:
        utctime = datetime.utcnow()
        utctime = utctime.strftime("%Y-%m-%d %H:%M:%S")
        orderOption.end = utctime
    if orderOption.goodName is not None:
        check = "%" + orderOption.goodName + "%"
        db_item = db.query(model.goods).filter(model.goods.name.like(check)).all()
        if db_item is None or db_item==[]:
            return []
        if orderOption.provider is not None:
            result=[]
            for good in db_item:
                result.append( db.query(model.OrderRecord).filter(model.OrderRecord.goodId == good.id).filter(
                model.OrderRecord.provider_id == orderOption.provider))
        else:
            result=[] #存储的是query
            for good in db_item:
                 result.append(db.query(model.OrderRecord).filter(model.OrderRecord.goodId == good.id))
        temp=[]#存储query.all()
        for i in result:
            result1=i.filter(model.OrderRecord.time >= orderOption.start).filter(
                model.OrderRecord.time <= orderOption.end).order_by(model.OrderRecord.time.desc()).all()
            for order in result1:
                for good in db_item:
                    if good.id==order.goodId:
                        name=good.name
                        break;
                setattr(order, "goodName", name)
                temp.append(order)
        result=temp
    else:
        result = db.query(model.OrderRecord).filter(model.OrderRecord.provider_id == orderOption.provider)
        result = result.filter(model.OrderRecord.time >= orderOption.start).filter(
            model.OrderRecord.time <= orderOption.end).order_by(model.OrderRecord.time.desc()).all()

    return result


@recore_subapi.get("/getRecordByName/{name}")
def getRecordByName(name: str, db: Session = Depends(crud.get_db)):
    check = "%" + name + "%"
    db_item = db.query(model.goods).filter(model.goods.name.like(check)).all()
    if db_item is None or db_item==[]:
        return []
    result = []
    for good in db_item:
        db_record = db.query(model.OrderRecord).filter(model.OrderRecord.goodId == good.id).all()
        for order in db_record:
            setattr(order, "goodName", good.name)
            result.append(order)
    # if result is None or result ==[]:
    #     raise HTTPException(status_code=400, detail="No such record about this goods")

    return result


@recore_subapi.post("/")
def createOrderRecord(order: schema.OrderRecordCreate, db: Session = Depends(crud.get_db)):
    return crud.create_orderRecord(db, order)
