from passlib.context import CryptContext

_pwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


def getEncryptStr(raw: str) -> str:
    return _pwdContext.hash(raw)


def bcryptVerify(raw: str, encryptedString: str) -> bool:
    return _pwdContext.verify(raw, encryptedString)
