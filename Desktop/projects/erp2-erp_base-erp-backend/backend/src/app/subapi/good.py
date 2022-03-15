from datetime import datetime
from fastapi import FastAPI, Response, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import crud, model, schema, jwtUtils, bcryptUtils
from ..crud import get_db
good_subapi =APIRouter()


@good_subapi.get("/getAllGoods/{page}", status_code=200)
def get_goods(page: int, db: Session = Depends(crud.get_db)):
    count = db.query(func.count(model.goods.id)).scalar()
    skip = (page - 1) * 10
    limit = 10
    data={
        "count":count,
        "data":db.query(model.goods).offset(skip).limit(limit).all()
    }
    return data


@good_subapi.put("/addGood/{goodId}", status_code=200)
def updateGood(goodId: int, update_item: schema.GoodUpdate, db: Session = Depends(get_db)):
    updated_item = crud.update_good(db, goodId, update_item)
    if updated_item is None or updated_item==[]:
        raise HTTPException(status_code=400, detail="Item not found")
    return updated_item


@good_subapi.get("/getGoodById/{good_id}", status_code=200)
def getGoodById(good_id: int, db: Session = Depends(crud.get_db)):
    result = db.query(model.goods).filter(model.goods.id == good_id).first()
    if result is None or result ==[]:
        return Response('Item not found', 400, media_type='application/json')
    return result


@good_subapi.post("/getGoodByTime", status_code=200)
def getGoodByTime(goodtime: schema.GoodTime, db: Session = Depends(get_db)):
    if goodtime.start is None:
        raise HTTPException(status_code=400, detail="please give a start time ")
    if goodtime.end is None:
        utctime = datetime.utcnow()
        utctime = utctime.strftime("%Y-%m-%d %H:%M:%S")
        goodtime.end = utctime
    return db.query(model.goods).filter(model.goods.time >= goodtime.start).filter(
        model.goods.time <= goodtime.end).order_by(model.goods.time.desc()).all()


@good_subapi.post("/getGoodByOptions", status_code=200)
def getGoodByOptions(goodOption: schema.GoodOption, db: Session = Depends(crud.get_db)):
    if goodOption.end is None:
        utctime = datetime.utcnow()
        utctime = utctime.strftime("%Y-%m-%d %H:%M:%S")
        goodOption.end = utctime

    result = db.query(model.goods).filter(model.goods.name == goodOption.name).filter(
        model.goods.name == goodOption.name).filter(model.goods.time >= goodOption.start).filter(
        model.goods.time <= goodOption.end).order_by(model.goods.time.desc()).all()
    return result


@good_subapi.delete("/{goodId}", status_code=200)
def deleteGood(goodId: int, db: Session = Depends(crud.get_db)):
    db.query(model.goods).filter(model.goods.id == goodId).delete()
    db.commit()
    db.close()


@good_subapi.post("/deleteGood/{good_id}")
def deleteGood(good_id: int, db: Session = Depends(crud.get_db)):
    db.query(model.goods).filter(model.goods.id == good_id).delete()
    db.commit()
    db.close()


@good_subapi.post("/", status_code=200)
def createGood(good: schema.GoodCreate, db: Session = Depends(get_db)):
    return crud.create_good(db=db, good=good)


@good_subapi.put("/{goodId}", status_code=200)
def updateGood(goodId: int, update_item: schema.GoodUpdateData, db: Session = Depends(get_db)):
    updated_item = crud.update_good_data(db, goodId, update_item)
    if updated_item is None:
        raise HTTPException(status_code=400, detail="Item not found")
    return updated_item


@good_subapi.get("/{goodName}", status_code=200)
def getGoodByName(goodName: str, db: Session = Depends(crud.get_db)):
    check="%"+goodName+"%"
    result = db.query(model.goods).filter(model.goods.name.like(check)).all()
    if result is None:
        return Response('Item not found', 400, media_type='application/json')
    return result


__all__ = ["good_subapi"]
