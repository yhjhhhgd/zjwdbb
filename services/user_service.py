from models import User


def get_user(session, uid, name):
    user = session.get(User, uid)
    if not user:
        user = User(user_id=uid, username=name)
        session.add(user)
        session.commit()
    return user
