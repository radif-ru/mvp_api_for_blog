from secrets import token_hex


def gen_token(nbytes=16) -> str:
    """ Сгенерировать токен """
    token: str = f'SuperToken {token_hex(nbytes=nbytes)}'
    return token
