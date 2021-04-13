from accounts.models import User

def run():
    for user in User.objects.all():
        user.JokerUsed = None
        user.save()