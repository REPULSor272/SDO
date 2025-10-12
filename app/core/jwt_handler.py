import jwt
from datetime import datetime, timedelta
from typing import Optional, Union
from app.config.config import init_config


config = init_config()['jwt']

SECRET_KEY = config["secret_key"]
ALGORITHM = config["algorithm"]
EXPIRES_IN = config["expires_in"]  # Время жизни токена в секундах


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Генерация JWT-токена.
    :param data: Данные, которые будут зашифрованы в токене.
    :param expires_delta: Время жизни токена (timedelta). Если None, берётся значение из конфига.
    :return: Сгенерированный токен.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(seconds=int(EXPIRES_IN)))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Union[dict, str]:
    """
    Декодирование JWT-токена.
    :param token: Токен для декодирования.
    :return: Декодированные данные токена или str, если токен недействителен.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return "Token has expired."
    except jwt.InvalidTokenError:
        return "Invalid token."
