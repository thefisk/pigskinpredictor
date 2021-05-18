from predictor.models import Prediction
from accounts.models import User
import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def run(hours):
    week = os.environ['PREDICTWEEK']
    season = os.environ['PREDICTSEASON']
    predweek = int(season+week)
    haspicked = []
    for pred in Prediction.objects.filter(PredWeek=predweek):
        if pred.User.id not in haspicked:
            haspicked.append(pred.User.id)
    nopreds = User.objects.exclude(id__in=haspicked)
    email_list = []
    for user in nopreds:
        email_list.append(user.email)
    if int(hours) == 48:
        optedinemails = []
        optedinusers = User.objects.filter(Reminder48=True)
        for i in optedinusers:
            optedinemails.append(i.email)
        for i in email_list:
            if i not in optedinemails:
                email_list.remove(i)
    
    templatefile = "email_reminder.html"
    html_message = render_to_string(templatefile)
    
    subject = "Pigskin Predictor: " + hours + " hour reminder"
    plaintextmessage = "This is your " + hours + " reminder to submit your predictions for week " + week

    msg = EmailMultiAlternatives(subject = subject, body = plaintextmessage, from_email = "Pigskin Predictor", to = ('Pigskin Predictor Users', "thepigskinpredictor@gmail.com"), bcc = email_list)
    msg.attach_alternative(html_message, "text/html")
    msg.send()