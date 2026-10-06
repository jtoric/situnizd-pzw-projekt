import bcrypt


def hash_password(plain: str) -> str:
    # gensalt stvara novi salt i upisuje ga u rezultat, uz algoritam i faktor rada
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()
