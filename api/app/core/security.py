import bcrypt


def hash_password(plain: str) -> str:
    # gensalt stvara novi salt i upisuje ga u rezultat, uz algoritam i faktor rada
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    # checkpw iz zapisa iščita salt i faktor rada, ponovi izračun i usporedi
    # u stalnom vremenu, pa iz trajanja usporedbe ništa ne slijedi
    return bcrypt.checkpw(plain.encode(), hashed.encode())
