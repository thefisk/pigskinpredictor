from celery import shared_task
from .models import Prediction
from accounts.models import User
from django.core.mail import EmailMessage
from django.template.loader import get_template
import os, requests, json, boto3, time
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from predictor.models import Team, Results, ScoresSeason, ScoresAllTime, ScoresWeek, Prediction, AvgScores
from django.core.cache import cache
from .cacheflushlist import cachestoflush

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
    if int(week) > 18:
        pass
    else:
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
            email_list_copy = email_list.copy()
            for i in email_list:
                if i not in optedinemails:
                    email_list_copy.remove(i)
            email_list = email_list_copy.copy
        
        # Below print will show on Celery output as a 'warning'
        # Kept in as it is useful logging because addresses are BCCd
        print(f"Emails going out to: {email_list}")
        
        templatefile = "email_reminder.html"
        html_message = render_to_string(templatefile)
        
        subject = "Pigskin Predictor: " + hours + " hour reminder"
        plaintextmessage = "This is your " + hours + " reminder to submit your predictions for week " + week

        msg = EmailMultiAlternatives(subject = subject, body = plaintextmessage, from_email = "Pigskin Predictor", to = ('Pigskin Predictor Users', "thepigskinpredictor@gmail.com"), bcc = email_list)
        msg.attach_alternative(html_message, "text/html")
        msg.send()

@shared_task
def save_results():
    resultsweek = os.environ['RESULTSWEEK']
    if int(resultsweek) > 18:
        pass
    else:
        if int(resultsweek) < 10:
            fileweek = '0'+resultsweek
        else:
            fileweek = resultsweek
        fileseason = os.environ['PREDICTSEASON']
        filename = 'data/resultsimport_'+fileseason+'_'+fileweek+'.json'
        bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')

        s3 = boto3.resource('s3')
        obj = s3.Object(bucket,filename)
        body = obj.get()['Body'].read().decode('utf-8')
        data = json.loads(body)

        # Save Results
        for result in data:
            dataHome = result.get('fields').get('HomeTeam')
            dataAway = result.get('fields').get('AwayTeam')
            dataWinner = result.get('fields').get('Winner')
            dataHomeScore = result.get('fields').get('HomeScore')
            dataAwayScore = result.get('fields').get('AwayScore')
            dataGameID = result.get('pk')
            actualHome = Team.objects.get(ShortName=dataHome)
            actualAway = Team.objects.get(ShortName=dataAway)
            newresult = Results(Season=fileseason,Week=fileweek,GameID=dataGameID,HomeTeam=actualHome,AwayTeam=actualAway,HomeScore=dataHomeScore,AwayScore=dataAwayScore, Winner=dataWinner)
            newresult.save()

        # Update Season extended stats 
        for score in ScoresSeason.objects.filter(Season=os.environ['PREDICTSEASON']):
            # Try / Except needed if a user misses a week
            try:
                weekscore = ScoresWeek.objects.get(Season=os.environ['PREDICTSEASON'], User=score.User, Week=os.environ['RESULTSWEEK'])
            except ScoresWeek.DoesNotExist:
                pass
            else:
                # Update WorstWeek if needed
                if weekscore.WeekScore < score.SeasonWorst:
                    score.SeasonWorst = weekscore.WeekScore
                # Update BestWeek if needed
                if weekscore.WeekScore > score.SeasonBest:
                    score.SeasonBest = weekscore.WeekScore
                # Recalculate Season Percentage
                seasoncorrect = Prediction.objects.filter(PredSeason=os.environ['PREDICTSEASON'], User=score.User, Points__gt=0).count()
                seasonpredcount = Prediction.objects.filter(PredSeason=os.environ['PREDICTSEASON'], User=score.User).exclude(Points__isnull=True).count()
                score.SeasonPercentage = (seasoncorrect/seasonpredcount)*100
                # Recalculate Season Average
                score.SeasonAverage = score.SeasonScore/ScoresWeek.objects.filter(Season=os.environ['PREDICTSEASON'], User=score.User).count()
                # Recalculate Banker Average
                banktotal = 0
                for banker in Prediction.objects.filter(PredSeason=os.environ['PREDICTSEASON'], User=score.User, Banker=True):
                    if isinstance(banker.Points, int):
                        banktotal += banker.Points
                score.BankerAverage=banktotal/Prediction.objects.filter(PredSeason=os.environ['PREDICTSEASON'], User=score.User, Banker=True).exclude(Points__isnull=True).count()
                score.save()

        # Update AllTime extended stats 
        for alltime in ScoresAllTime.objects.all():
            # Try / Except needed if a user misses a week
            try:
                weekscore = ScoresWeek.objects.get(Season=os.environ['PREDICTSEASON'], User=alltime.User, Week=os.environ['RESULTSWEEK'])
            except ScoresWeek.DoesNotExist:
                pass
            else:
                # Update WorstWeek if needed
                if weekscore.WeekScore < alltime.AllTimeWorst:
                    alltime.AllTimeWorst = weekscore.WeekScore
                # Update BestWeek if needed
                if weekscore.WeekScore > alltime.AllTimeBest:
                    alltime.AllTimeBest = weekscore.WeekScore
                # Recalculate Season Percentage
                alltimecorrect = Prediction.objects.filter(User=alltime.User, Points__gt=0).count()
                alltimepredcount = Prediction.objects.filter(User=alltime.User).exclude(Points__isnull=True).count()
                alltime.AllTimePercentage = (alltimecorrect/alltimepredcount)*100
                # Recalculate Season Average
                alltime.AllTimeAverage = alltime.AllTimeScore/ScoresWeek.objects.filter(User=alltime.User).count()
                # Recalculate Banker Average
                alltimebanktotal = 0
                for alltimebanker in Prediction.objects.filter(User=alltime.User, Banker=True):
                    if isinstance(alltimebanker.Points, int):
                        alltimebanktotal += alltimebanker.Points
                alltime.AllTimeBankerAverage=alltimebanktotal/Prediction.objects.filter(User=alltime.User, Banker=True).exclude(Points__isnull=True).count()
                alltime.save()

        # Add latest positional data to each user profile
        scorecounter = 1
        positiondict = {}
        usercount = User.objects.all().count() -1
        for i in ScoresSeason.objects.all():
            positiondict[i.User.pk]=scorecounter
            scorecounter += 1
        if int(resultsweek) == 1:
            for i in User.objects.all():
                # Create season object before adding to it in week 1
                i.Positions = {"data":{str(fileseason):{}}}
                try:
                    i.Positions['data'][str(fileseason)][str(resultsweek)] = positiondict[i.pk]
                except(KeyError):
                    # Make position bottom of table if they didn't play in week 1
                    i.Positions['data'][str(fileseason)][str(resultsweek)] = usercount
                i.save()
        else:
            for i in User.objects.all():
                try: 
                    i.Positions['data'][str(fileseason)][str(resultsweek)] = positiondict[i.pk]
                except(KeyError):
                    # Make position bottom of table if they still didn't play
                    i.Positions['data'][str(fileseason)][str(resultsweek)] = usercount
                i.save()

        # Add latest AvgScores
        totalscores = 0
        count = 0
        for i in ScoresWeek.objects.filter(Season=int(os.environ['PREDICTSEASON']), Week=int(os.environ['RESULTSWEEK'])):
            totalscores += i.WeekScore
            count +=1
        latestavg = int(totalscores/count)
        try:
            Avgs = AvgScores.objects.get(Season=int(fileseason))
            Avgs.AvgScores[str(resultsweek)] = latestavg
            Avgs.save()
        except AvgScores.DoesNotExist:
            NewDict = {}
            NewDict[str(resultsweek)] = latestavg
            NewAvgs = AvgScores(Season=int(fileseason), AvgScores=NewDict)
            NewAvgs.save()


        # Finally, clear the Redis caches
        for c in cachestoflush:
            cache.delete(c)


@shared_task
def fetch_results(fetchonly):
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
    
    if int(fetchonly) == 1:
        pass
    elif int(fetchonly) == 0:
        # Call Save Results once file is uploaded to S3
        # 30 second delay to let S3 sort itself out and ensure file is ready
        time.sleep(30)
        save_results()

@shared_task
def joker_reset():
    for user in User.objects.all():
        user.JokerUsed = None
        user.save()