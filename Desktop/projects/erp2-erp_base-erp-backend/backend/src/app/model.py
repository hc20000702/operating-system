from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String,BigInteger,ForeignKey,TIMESTAMP,DATETIME,TIME,BLOB
from sqlalchemy.orm import sessionmaker,relationship
from src.app.database import SqlalchemyDatabaseUrl
engine = create_engine(SqlalchemyDatabaseUrl)
Base = declarative_base(engine)  # SQLORM基类
session = sessionmaker(engine)()  # 构建session对象



class User(Base):
    __tablename__='user'
    id=Column(Integer,primary_key=True,autoincrement=True)
    status=Column(Integer)# 0common，1admin，2su
    account=Column(String(50),unique=True)
    pwd=Column(String(255))
    accountStatus=Column(Integer)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class goods(Base):
    __tablename__='goods'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name=Column(String(100))
    time=Column(DATETIME)
    # classification=Column(Integer)
    storage=Column(BigInteger)
    description=Column(String(100))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}



class order(Base):
    __tablename__='order'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time=Column(DATETIME)
    # good_id=Column(Integer,ForeignKey("goods.id"))
    amount=Column(Integer)
    goodId=Column(Integer,ForeignKey("goods.id",ondelete='CASCADE'))
    OrderStatus=Column(Integer)# 0未处理，1处理成功，2 退货
    source=Column(String(40))
    description=Column(String(255))
    BuyerInfo=Column(BlOB)

    # customer = relationship("customer", back_populates="owner")
    # commodity=relationship("goods", back_populates="o")
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class OrderRecord(Base):
    __tablename__='OrderRecord'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time=Column(DATETIME)
    provider_id=Column(String(100))
    goodId = Column(Integer,ForeignKey("goods.id",ondelete='CASCADE'))
    amount = Column(Integer)
    # commodity = relationship("goods", back_populates="owner")
#商户
class Customer(Base):
    __tablename__='Customer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    phoneNumber=Column(String(15))
    openApi=Column(BLOB)



Base.metadata.drop_all()
Base.metadata.create_all()  # 将模型映射到数据库中


