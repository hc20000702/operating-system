import json
from datetime import datetime
import pika
from fastapi.openapi.models import Response
from sqlalchemy.orm import Session
from fastapi import HTTPException
from starlette import status
from . import model, schema
import time
from . import bcryptUtils

# Dependency
from .database import SessionLocal

config = pika.ConnectionParameters(
    host='amqp-x4eb2p4p44j9.rabbitmq.ap-gz.public.tencenttdmq.com',
    port=5672,
    virtual_host='amqp-x4eb2p4p44j9|test',
    credentials=pika.PlainCredentials(
        'tester',
        'eyJrZXlJZCI6ImFtcXAteDRlYjJwNHA0NGo5IiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiJhbXFwLXg0ZWIycDRwNDRqOV90ZXN0ZXIifQ.vZgg6GEzzuqKaSRg4n7RRguqcI9rl7NrTLRcSZJqNeo')
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# 根据传入的account筛选user
def getUserByAccount(db: Session, userAccount: str):
    return db.query(model.User).filter(model.User.account == userAccount).first()


def getUserByID(db: Session, user_id: int):
    return db.query(model.User).filter(model.User.id == user_id).first()


def createUser(db: Session, user: schema.UserCreate):
    # 新建user，根据UserCreate来验证传入的数据
    fake_pwd = bcryptUtils.getEncryptStr(user.pwd)
    db_user = model.User(account=user.account, pwd=fake_pwd, status=user.status)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return Response('success', 200, media_type='application/json')


def updateUser(db: Session, account: str, update_user: schema.UserUpdate, ):
    db_user = db.query(model.User).filter(model.User.account == account).first()
    if db_user:
        update_user.pwd = bcryptUtils.getEncryptStr(update_user.pwd)
        update_dict = update_user.dict(exclude_unset=True)
        for k, v in update_dict.items():
            setattr(db_user, k, v)
        db.commit()
        db.flush()
        db.refresh(db_user)
        raise HTTPException(status_code=status.HTTP_200_OK, detail='success')


def getGoodById(db: Session, goodId: int):
    return db.query(model.goods).filter(model.goods.id == goodId).first()


def create_good(db: Session, good: schema.GoodCreate):
    result = db.query(model.goods).filter(model.goods.name == good.name).first()
    if result is not None and result!=[]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='this goodName has been used')
    utctime = datetime.utcnow()
    utctime = utctime.strftime("%Y-%m-%d %H:%M:%S")
    db_good = model.goods(name=good.name, storage=0, description=good.description, time=utctime)
    db.add(db_good)
    db.commit()
    db.refresh(db_good)
    raise HTTPException(status_code=status.HTTP_200_OK, detail='success')


def update_good_data(db: Session, good_id: int, update_item: schema.GoodUpdateData):
    db_item = db.query(model.goods).filter(model.goods.id == good_id).first()
    if db_item==[] or db_item is None:
       raise HTTPException(status_code=400, detail="Item not found")
    utctime = datetime.utcnow()
    utctime = utctime.strftime("%Y-%m-%d %H:%M:%S")
    setattr(db_item, "time", utctime)
    if update_item.name is not None:
        setattr(db_item, "name", update_item.name)
    setattr(db_item, "description", update_item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_good(db: Session, good_id: int, update_item: schema.GoodUpdate):
    utctime = datetime.utcnow()
    utctime = utctime.strftime("%Y-%m-%d %H:%M:%S")
    db_orderRecord = model.OrderRecord(amount=update_item.addAmount, time=utctime, goodId=good_id,
                                       provider_id=update_item.provider)
    db_item = db.query(model.goods).filter(model.goods.id == good_id).first()
    storage = db_item.storage + update_item.addAmount
    if db_item is None or db_item==[]:
        raise HTTPException(status_code=400, detail="the goods is not exist,please first ccreate goods")
    data = {
            "type": "updateGood",
            "storage": storage,
            "goodId": good_id
        }
    # connection是一个Disposable对象，要么，你就要手动去关闭它，要么就必须使用with关键字来自动关闭它
    with pika.BlockingConnection(config) as connection:
        channel = connection.channel()
        # 参数分别是exchange、routing_key和消息体，最后一个是属性，delivery mode = 1表示这条消息需要持久化
        channel.basic_publish(
            'storageChange',
            'modify',
            json.dumps(data),
            pika.BasicProperties(delivery_mode=1)
        )
    utctime = datetime.utcnow()
    utctime = utctime.strftime("%Y-%m-%d %H:%M:%S")
    db.add(db_orderRecord)
    db.commit()
    db.refresh(db_orderRecord)
    a=db_item.storage
    setattr(db_item, "time", utctime)
    setattr(db_item, "storage", storage)
    return db_item


def get_order_by_id(db: Session, id: int):
    return db.query(model.order).filter(model.order.id == id).first()


def create_order(db: Session, order: schema.OrderCreate):
    utctime = datetime.utcnow()
    utctime = utctime.strftime("%Y-%m-%d %H:%M:%S")
    db_item = db.query(model.goods).filter(model.goods.id == order.goodId).first()
    if db_item is None or db_item==[]:
        raise HTTPException(status_code=400, detail="the goods is not exist,please first create goods")
    db_order = model.order(amount=order.amount, time=utctime, goodId=order.goodId,
                           OrderStatus=0, source=order.source, description=order.description)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    # execute_order(db,order)
    return db_order


def execute_order(db: Session, order: schema.OrderExe):
    db_order = db.query(model.order).filter(model.order.id == order.id).first()
    if db_order is None or db_order==[]:
        raise HTTPException(status_code=400, detail='order is not create')
    if db_order.OrderStatus == 1:
        raise HTTPException(status_code=400, detail="order has already been execute")
    db_item = db.query(model.goods).filter(model.goods.id == db_order.goodId).first()

    if db_item:
        update = db_item.storage - db_order.amount
        data = {
            "type": "executeOrder",
            "orderId": order.id
        }
        # connection是一个Disposable对象，要么，你就要手动去关闭它，要么就必须使用with关键字来自动关闭它
        with pika.BlockingConnection(config) as connection:
            channel = connection.channel()
            # 参数分别是exchange、routing_key和消息体，最后一个是属性，delivery mode = 1表示这条消息需要持久化
            channel.basic_publish(
                'storageChange',
                'modify',
                json.dumps(data),
                pika.BasicProperties(delivery_mode=1)
            )
        name = "storage"
        utctime = datetime.utcnow()
        utctime = utctime.strftime("%Y-%m-%d %H:%M:%S")
        setattr(db_item, "time", utctime)
        setattr(db_item, name, update)
        return db_item
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="order is not exist")


def str_to_timestamp(str_time=None, format="%Y-%m-%d %H:%M:%S"):
    if str_time:
        time_tuple = time.strptime(str(str_time), format)
        return int(time.mktime(time_tuple))
    return int(time.time())


def create_orderRecord(db: Session, order: schema.OrderRecordCreate):
    utctime = datetime.utcnow()
    utctime = utctime.strftime("%Y-%m-%d %H:%M:%S")
    db_orderRecord = model.OrderRecord(amount=order.amount, time=utctime, goodId=order.good_id,
                                       provider_id=order.provider)

    db_item = db.query(model.goods).filter(model.goods.id == order.good_id).first()
    if db_item is None or db_item==[]:
        raise HTTPException(status_code=400, detail="the goods is not exist,please first create goods")

    data = {
        "type": "createOrderRecord",
        "goodId": order.good_id,
        "amount": order.amount
    }

    with pika.BlockingConnection(config) as connection:
        channel = connection.channel()
        # 参数分别是exchange、routing_key和消息体，最后一个是属性，delivery mode = 1表示这条消息需要持久化
        channel.basic_publish(
            'storageChange',
            'modify',
            json.dumps(data),
            pika.BasicProperties(delivery_mode=1)
        )
    db.add(db_orderRecord)
    db.commit()
    db.refresh(db_orderRecord)
    update = db_item.storage + order.amount
    utctime = datetime.utcnow()
    utctime = utctime.strftime("%Y-%m-%d %H:%M:%S")
    setattr(db_item, "time", utctime)
    setattr(db_item,"storage", update)
    return db_item
