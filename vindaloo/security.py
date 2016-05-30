def get_authenticated_user(request):
    username = request.unauthenticated_userid
    if username:
        # TODO: implement this properly, requires a proper User model.
        User = None
        return request.dbsession.query(User).filter(User.username == username).first()
