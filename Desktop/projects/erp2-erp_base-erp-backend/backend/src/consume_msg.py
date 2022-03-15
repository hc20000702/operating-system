import json
from datetime import datetime
import pika
from app import model
from app.crud import get_db

config = pika.ConnectionParameters(
    host='amqp-x4eb2p4p44j9.rabbitmq.ap-gz.public.tencenttdmq.com',
    port=5672,
    virtual_host='amqp-x4eb2p4p44j9|test',
    credentials=pika.PlainCredentials(
        'tester',
        'eyJrZXlJZCI6ImFtcXAteDRlYjJwNHA0NGo5IiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiJhbXFwLXg0ZWIycDRwNDRqOV90ZXN0ZXIifQ.vZgg6GEzzuqKaSRg4n7RRguqcI9rl7NrTLRcSZJqNeo')
)


# 消费者的方法，当有消息来的时候，调用这个方法
def executeOrder(order_id: id):
    db = next(get_db())
    db_order = db.query(model.order).filter(model.order.id == order_id).first()
    if(db_order==None):return True
    if db_order.OrderStatus==1:
        return True
    db_item = db.query(model.goods).filter(model.goods.id == db_order.goodId).first()
    update = db_item.storage - db_order.amount
    utctime = datetime.utcnow()
    utctime = utctime.strftime("%Y-%m-%d %H:%M:%S")
    setattr(db_item, "time", utctime)
    setattr(db_item, "storage", update)
    setattr(db_order, "OrderStatus", 1)
    db.commit()
    db.flush()
    db.refresh(db_item)
    db.refresh(db_order)
    return True


def createOrderRecord(good_id: int, amount: int):
    db = next(get_db())
    db_item = db.query(model.goods).filter(model.goods.id == good_id).first()

    update = db_item.storage + amount
    name = "storage"
    utctime = datetime.utcnow()
    utctime = utctime.strftime("%Y-%m-%d %H:%M:%S")
    setattr(db_item, "time", utctime)
    setattr(db_item, name, update)
    db.commit()
    db.flush()
    db.refresh(db_item)
    return True


def updateGood(storage:int,good_id:int):
    db = next(get_db())
    db_item = db.query(model.goods).filter(model.goods.id == good_id).first()
    if db_item:
        utctime = datetime.utcnow()
        utctime = utctime.strftime("%Y-%m-%d %H:%M:%S")
        setattr(db_item, "time", utctime)
        setattr(db_item, "storage", storage)
        db.commit()
        db.flush()
        db.refresh(db_item)
    print(db_item)
    return True


def on_message(channel, method_frame, header_frame, body):
    # 消息是存在body里的，method frame和header frame在此处不是很重要
    # body是以字节的形式呈现的
    data = json.loads(body)
    print(data['type'])
    flag = 0
    if data['type'] == "executeOrder":
        flag = executeOrder(data["orderId"])
    elif data['type'] == "createOrderRecord":
        flag = createOrderRecord(data["goodId"], data["amount"])
    elif data['type'] == "updateGood":
        flag = updateGood(data["storage"],data["goodId"])

    # 处理完了，告诉消息队列这个消息成功处理掉了
    if flag == 1:
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

# connection是一个Disposable对象，要么，你就要手动去关闭它，要么就必须使用with关键字来自动关闭它
with pika.BlockingConnection(config) as connection:
    channel = connection.channel()

    # qos是一个流控参数，表示这个消费者一次只预取一条消息，当然你也可以不设置，不是很影响
    channel.basic_qos(prefetch_count=1)

    # 定义一个消费者，第一个参数是queue，第二个参数是消息到达后调用的处理函数，第三个是自动确认，这个必须设为false
    # 自动确认为true的时候，rabbitmq直接把数据扔给消费者之后，它就不管了，不管你处理成不成功，它都不管了
    # 这个在这种重视CP的系统里头，这显然是不合适的，会丢数据
    # 如果不自动确认的话，rabbitmq会直到你调用basic_ack方法的时候，才确认消息被处理成功了，这就比较安全了
    channel.basic_consume(
        'modifyChanges',
        on_message,
        auto_ack=False
    )

    # 开始消费，但是这是一个阻塞方法，永远不会结束的，不要在业务逻辑中写
    channel.start_consuming()
