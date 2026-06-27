from ..config import ADMIN_IDS

def is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS
