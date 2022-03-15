from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import crud, model, schema, jwtUtils, bcryptUtils
from ..crud import get_db
order_subapi = APIRouter()


@order_subapi.post("/executeOrder")
def executeOrder(order: schema.OrderExe, db: Session = Depends(get_db)):
    return crud.execute_order(db=db, order=order)


@order_subapi.get("/getAllOrders/{page}")
def get_orders(page: int, db: Session = Depends(crud.get_db)):
    count = db.query(func.count(model.order.id)).scalar()
    skip = (page - 1) * 10
    limit = 10
    result = db.query(model.order).offset(skip).limit(limit).all()
    for order in result:
        good = crud.getGoodById(db, order.goodId)
        setattr(order, "goodName", good.name)
    data={
        "count":count,
        "data":result
    }
    return data


@order_subapi.post("/getOrderByTime", status_code=200)
def getOrderByTime(ordertime: schema.OrderTime, db: Session = Depends(crud.get_db)):
    if ordertime.start is None:
        raise HTTPException(status_code=400, detail="please give a start time ")
    if ordertime.end is None:
        utctime = datetime.utcnow()
        utctime = utctime.strftime("%Y-%m-%d %H:%M:%S")
        ordertime.end = utctime
    result = db.query(model.order).filter(model.order.time >= ordertime.start).filter(
        model.order.time <= ordertime.end).order_by(model.order.time.desc()).all()
    for order in result:
        good = crud.getGoodById(db, order.goodId)
        setattr(order, "goodName", good.name)
    return result


@order_subapi.get("/getOrderByGoodName/{goodName}", status_code=200)
def getOrderByGoodName(goodName: str, db: Session = Depends(crud.get_db)):
    check = "%" + goodName + "%"
    db_item = db.query(model.goods).filter(model.goods.name.like(check)).all()
    if db_item is None or db_item == []:
        return []
    result = []
    for good in db_item:
        db_record = db.query(model.order).filter(model.order.goodId == good.id).all()
        for order in db_record:
            setattr(order, "goodName", good.name)
            result.append(order)
    # if result is None or result ==[]:
    #     raise HTTPException(status_code=400, detail="No such order about this goods")
    return result


@order_subapi.post("/getOrderByOptions", status_code=200)
def getOrderByOptions(orderOption: schema.orderOption, db: Session = Depends(crud.get_db)):
    # goodName:str
    # orderId:int=0
    # start: str
    # end: str = None
    if orderOption.end is None:
        utctime = datetime.utcnow()
        utctime = utctime.strftime("%Y-%m-%d %H:%M:%S")
        orderOption.end = utctime
    check = "%" + orderOption.goodName + "%"
    db_item = db.query(model.goods).filter(model.goods.name.like(check)).all()
    if db_item is None or db_item == []:
        return []
    if orderOption.orderId == 0:
        result = []
        for good in db_item:
            db_record = db.query(model.order).filter(model.order.goodId == good.id).filter(
                model.order.time >= orderOption.start).filter(
                model.order.time <= orderOption.end).order_by(model.order.time.desc()).all()
            for order in db_record:
                setattr(order, "goodName", good.name)
                result.append(order)
    else:
        result = []
        for good in db_item:
            db_record = db.query(model.order).filter(
                model.order.id == orderOption.orderId).filter(model.order.goodId == good.id).filter(
                model.order.time >= orderOption.start).filter(
                model.order.time <= orderOption.end).order_by(model.order.time.desc()).all()
            for order in db_record:
                setattr(order, "goodName", good.name)
                result.append(order)

    return result


@order_subapi.get("/{id}")
def getOrderById(id: int, db: Session = Depends(get_db)):
    db_order = crud.get_order_by_id(db, id)
    if db_order == [] or db_order is None:
        return []
    good = crud.getGoodById(db, db_order.goodId)
    setattr(db_order, "goodName", good.name)
    return db_order


@order_subapi.post("/deleteOrder/{order_id}")
def deleteOrder(order_id: int, db: Session = Depends(crud.get_db)):
    db.query(model.order).filter(model.order.id == order_id).delete()
    db.commit()
    db.close()


@order_subapi.post("/")
def createOrder(order: schema.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db=db, order=order)


@order_subapi.put("/{orderId}")
def updateOrder(orderId: int, order:schema.orderUpdate, db: Session = Depends(get_db)):
    db_order = crud.get_order_by_id(db, orderId)
    if db_order == [] or db_order is None:
        return []
    good = crud.getGoodById(db, db_order.goodId)
    setattr(db_order, "goodName", good.name)
    setattr(db_order, "description", order.description)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


__all__ = ["order_subapi"]
