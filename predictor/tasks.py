from celery import shared_task
from .models import Prediction
from accounts.models import User
from django.core.mail import EmailMessage
from django.template.loader import get_template
import os, requests, json, boto3
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

@shared_task
def email_confirmation(user, week, type):
    emailuser = User.objects.get(id=user)
    mypreds = Prediction.objects.filter(User=emailuser, PredWeek=week)
    address = []
    shortweek = str(week)[4::]
    if type =='New':
        heading = 'New Picks Are In'
    elif type == 'Amended':
        heading = 'Picks Successfully Amended'
    emailweek = 'Week ' + shortweek
    address.append(User.objects.get(id = user).email)
    subject = type + " Predictions Confirmed | Week " + shortweek
    from_email = "Pigskin Predictor"
    msg = EmailMessage(
        subject, 
        get_template('email_confirmation.html').render(
            {
                'heading': heading,
                'week': emailweek,
                'mypreds': mypreds,
            }
        ),
        from_email,
        address
    )
    msg.content_subtype = "html"
    msg.send()
    return None

@shared_task
def email_reminder(hours):
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

def test_func():
    print('Proof of Concept - this shows results save script can be called here after fetchresults completes')

@shared_task
def fetchresults():
    week = os.environ['RESULTSWEEK']
    season = os.environ['PREDICTSEASON']

    if int(week) < 10:
        filename = "resultsimport_"+season+"_0"+week+".json"
    else:
        filename = "resultsimport_"+season+"_"+week+"_.json"

    outfile = open(filename, "w")

    # Removed Thurs-Tues logic as below will produce a gameweek, no matter when it's requested
    source = f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={season}&week={week}"

    rawjson = requests.get(source).json()

    results = []

    for game in rawjson['events']:
        team1 = {}
        team1['team'] = game['competitions'][0]['competitors'][0]['team']['abbreviation']
        team1['score'] = int(game['competitions'][0]['competitors'][0]['score'])
        team1['location'] = game['competitions'][0]['competitors'][0]['homeAway']
        team2 = {}
        team2['team'] = game['competitions'][0]['competitors'][1]['team']['abbreviation']
        team2['score'] = int(game['competitions'][0]['competitors'][1]['score'])
        team2['location'] = game['competitions'][0]['competitors'][1]['homeAway']
        innerdict = {}
        innerdict["Week"] = int(week)
        innerdict["Season"] = int(season)
        if team1['location'] == "home":
            innerdict["HomeTeam"] = team1['team']
            innerdict["AwayTeam"] = team2['team']
            innerdict["HomeScore"] = team1['score']
            innerdict["AwayScore"] = team2['score']
        else:
            innerdict["HomeTeam"] = team2['team']
            innerdict["AwayTeam"] = team1['team']
            innerdict["HomeScore"] = team2['score']
            innerdict["AwayScore"] = team1['score']
        if team1['score'] == team2['score']:
            innerdict["Winner"] = "Tie"
        elif (team1['score']) > (team2['score']):
            innerdict["Winner"] = "Home"
        else:
            innerdict["Winner"] = "Away"
        outerdict = {}
        outerdict["model"] = "predictor.results"
        outerdict["pk"] = game['id']
        outerdict["fields"] = innerdict
        results.append(outerdict)

    # ESPN Uses different short names for Washington and LA Rams to NFL.com
    # Loop through and rename them to ensure they match our model
    # Otherwise the import won't work!

    for result in results:
        if (result['fields']['HomeTeam']) == "WSH":
            result['fields']['HomeTeam'] = "WAS"
        if (result['fields']['HomeTeam']) == "LAR":
            result['fields']['HomeTeam'] = "LA"
        if (result['fields']['AwayTeam']) == "WSH":
            result['fields']['AwayTeam'] = "WAS"
        if (result['fields']['AwayTeam']) == "LAR":
            result['fields']['AwayTeam'] = "LA"

    sortedresults = sorted(results, key=lambda k: k['pk'])
    jsonout = json.dumps(sortedresults)
    outfile.write(jsonout)
    outfile.close()

    # Upload to S3
    bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    s3 = boto3.resource('s3')
    s3path = 'data/'+filename
    s3.Object(bucket, s3path).upload_file(Filename=filename)
    # Calling another function here appears to work fine
    test_func()