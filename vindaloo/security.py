from .models import User


def get_authenticated_user(request):
    username = request.unauthenticated_userid
    if username:
        return request.dbsession.query(User).filter(User.username == username).first()
