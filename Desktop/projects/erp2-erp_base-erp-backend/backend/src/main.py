from fastapi import FastAPI, Request, Response, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
import uvicorn
from starlette.middleware.cors import CORSMiddleware

from app import model,schema,crud,jwtUtils
from app.database import engine
import re
from app.subapi.user import user_subapi
from app.subapi.order import order_subapi
from app.subapi.good import good_subapi
from app.subapi.record import recore_subapi

model.Base.metadata.create_all(bind=engine)

api_router = APIRouter()


@api_router.put("/user/")
def updateUser(request: Request, update_user: schema.UserUpdate, db: Session = Depends(crud.get_db)):
    token = ''
    try:
        token = request.headers['Authorization']
    except KeyError:
        pass

    try:
        token = request.headers['authorization']

    except KeyError:
        pass
    token = token[7:]
    if token != '':
        user_account = jwtUtils.getUserNameFromJwt(token)
        update = crud.updateUser(db, user_account, update_user)
    else:
        raise HTTPException(status_code=500, detail="please login!")
    if update is None or update==[]:
        raise HTTPException(status_code=404, detail="User not found")
    raise HTTPException(status_code=500, detail="success")

api_router.include_router(user_subapi, tags=['user'], prefix='/user')
api_router.include_router(order_subapi, tags=['Post'], prefix="/order")
api_router.include_router(good_subapi, tags=['Category'], prefix="/good")
api_router.include_router(recore_subapi, tags=['Comment'], prefix="/record")


baseApp = FastAPI()
baseApp.include_router(api_router, prefix='/api')

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # 允许访问的源
#     allow_credentials=True,  # 支持 cookie
#     allow_methods=["*"],  # 允许使用的请求方法
#     allow_headers=["*"]  # 允许携带的 Headers
# )

async def get_app():
    return baseApp


def regexMatch(pattern: str, target: str) -> bool:
    result = re.match(pattern, target, re.I)
    return result != None


@baseApp.middleware('http')
async def authorizationVerifier(request: Request, call_next):
    token = ''
    go = False
    try:
        token = request.headers['Authorization']
    except KeyError:
        pass

    try:
        token = request.headers['authorization']
    except KeyError:
        pass
    token = token[7:]
    print(token)

    # 没有提供jwt
    if token == '':
        matches = map(lambda x: regexMatch(x, request.url.path),
                      jwtUtils.AUTHORIZE_ROUTING_TABLE['white_list'])
        # 但符合白名单，放行
        if any(matches):
            go = True
    # 有提供jwt
    else:
        # 并且这个jwt还有用，接着检查权限
        if jwtUtils.verifyJwt(token):
            role = jwtUtils.getRoleFromJwt(token)
            matches = map(lambda x: regexMatch(x, request.url.path),
                          jwtUtils.AUTHORIZE_ROUTING_TABLE[role])
            # 权限足够，放行
            if any(matches):
                print(1)
                go = True

    # 允许放行的请求接着下一步
    if go:
        response = await call_next(request)
        return response
    # 不符合要求的直接短路
    else:
        return Response('invalid user!', 403, media_type='text/plain')


if __name__ == '__main__':
    uvicorn.run("main:baseApp", host="0.0.0.0", port=8000, log_level="info")
