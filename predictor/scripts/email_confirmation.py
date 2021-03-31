from predictor.models import Prediction
from accounts.models import User
from django.core.mail import EmailMessage
from django.template.loader import get_template

def email_confirmation(user, week, type):
    mypreds = Prediction.objects.filter(User=user, PredWeek=week)
    address = []
    shortweek = str(week)[4::]
    if type =='New':
        heading = 'New Picks Are In | Week ' + shortweek
    elif type == 'Amended':
        heading = 'Picks Successfully Amended | Week' + shortweek
    address.append(User.objects.get(id = user.id).email)
    subject = type + " Predictions Confirmed | Week " + shortweek
    from_email = "Pigskin Predictor"
    msg = EmailMessage(
        subject, 
        get_template('email_confirmation.html').render(
            {
                'heading': heading,
                'mypreds': mypreds,
                'user': user
            }
        ),
        from_email,
        address
    )
    msg.content_subtype = "html"
    msg.send()
