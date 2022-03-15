from pydantic import BaseModel


class UserBase(BaseModel):
    # 账户是否存在
    account: str


class UserCheck(UserBase):
    pwd: str


class UserCreate(BaseModel):
    account: str
    status: int
    pwd: str


class UserUpdate(BaseModel):
    pwd: str
    status: int


class User(UserBase):
    id: int
    pwd: str
    status: int

    class Config:
        orm_mod = True


class GoodBase(BaseModel):
    name: str
    storage: int
    description: str = None


class GoodCreate(BaseModel):
    name: str
    description: str = None


class GoodUpdateData(BaseModel):
    name: str = None
    description: str


class GoodUpdate(BaseModel):
    addAmount: int
    provider:str

class Good(GoodBase):
    description: str = None

    class Config:
        orm_mode = True


class GoodOption(BaseModel):
    name: str
    start: str
    end: str = None


class GoodTime(BaseModel):
    start: str
    end: str = None


class OrderBase(BaseModel):
    amount: int
    goodId: int
    source: str
    description: str


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    amount: int
    id: int
    good_id: int


class OrderExe(BaseModel):
    id: int


class Order(OrderBase):
    goodId: int
    time: str

    class Config:
        orm_mode = True


class OrderTime(BaseModel):
    start: str
    end: str = None


class orderOption(BaseModel):
    goodName: str
    orderId: int = 0
    start: str
    end: str = None

class orderUpdate(BaseModel):
    description: str
class OrderRecordCreate(BaseModel):
    good_id: int
    amount: int
    provider: str = None


class recordOption(BaseModel):
    goodName: str = None
    provider: str = None
    start: str
    end: str = None
