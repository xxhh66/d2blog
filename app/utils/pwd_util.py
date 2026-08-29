import bcrypt


def get_password_hash(password:str)->str:
    salt = bcrypt.gensalt(6)
    return bcrypt.hashpw(password.encode('utf-8'),salt=salt).decode('utf-8')