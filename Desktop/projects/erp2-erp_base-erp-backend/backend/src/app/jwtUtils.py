from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = '0c7171f2bdfd0613560ec5db17fae8b2013dd47a28b50c2338b4cfb3ede9f11b'
ALGORITHM = 'HS256'
TOKEN_VALID_DAYS = 2
ISSUER = 'kevinC.erp.plus'
AUTHORIZE_ROUTING_TABLE = {'common': ['/', ],
                           'admin': ['/'],
                           'su': ['/'],
                           'white_list': ['/', '/user/login/']}


class CredentialException(Exception):
    def __init__(self, name, reason):
        self.name = name
        self.reason = reason


def generateJwt(userName: str, role: str) -> str:
    payload = {'aud': userName, 'iss': ISSUER}
    if role not in AUTHORIZE_ROUTING_TABLE.keys():
        raise CredentialException(
            'wrong role claim', f'No such role named {role}')
    else:
        payload.update({'role': role})
    exp = datetime.utcnow() + timedelta(days=TOKEN_VALID_DAYS)
    payload.update({'exp': exp})
    return jwt.encode(payload, SECRET_KEY, ALGORITHM)


def verifyJwt(token: str) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM,
                             issuer=ISSUER, options={'verify_aud': False})
        return payload != None
    except JWTError:
        print("error")
        return False


def getUserNameFromJwt(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM,
                             issuer=ISSUER, options={'verify_aud': False})
        userName = payload['aud']
        if userName == None:
            raise CredentialException('wrong jwt', 'payload not exist!')
        return userName
    except JWTError:
        raise CredentialException('wrong jwt', 'jwt parse failed!')


def getRoleFromJwt(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM,
                             issuer=ISSUER, options={'verify_aud': False})
        userName = payload['role']
        if userName == None:
            raise CredentialException('wrong jwt', 'payload not exist!')
        return userName
    except JWTError:
        raise CredentialException('wrong jwt', 'jwt parse failed!')
