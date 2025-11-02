import datetime, sys, logging
from datetime import datetime as dt
from celery import shared_task
from .models import Prediction
from predictor.cacheflushlist import cachestoflush
from django.core.cache import cache
from accounts.models import User
from django.core.mail import EmailMessage
from django.template.loader import get_template
import os, requests, json, boto3, time, sys
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from predictor.models import Team, Results, ScoresSeason, ScoresAllTime, ScoresWeek, Prediction, AvgScores, LiveGame, Match, PigskinConfig, Banker

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
    from_email = "'Pigskin Predictor' <hello@pigskinpredictor.com>"
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
    week = PigskinConfig.objects.get(Name="live").PredictWeek
    if int(week) > 18 or os.environ['REMINDERS_ON'].upper() != "TRUE":
        pass
    else:
        season = PigskinConfig.objects.get(Name="live").PredictSeason
        predweek = int(str(season)+str(week))
        haspicked = []
        for pred in Prediction.objects.filter(PredWeek=predweek):
            if pred.User.id not in haspicked:
                haspicked.append(pred.User.id)
        # Add disabled users to exclusion list
        for user in User.objects.filter(is_active=False):
            haspicked.append(user.id)
        # Add site admin to exclusion list
        haspicked.append((User.objects.get(pk=1)).id)
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
            email_list = email_list_copy.copy()
        
        # Below print will show on Celery output as a 'warning'
        # Kept in as it is useful logging because addresses are BCCd
        print(f"Emails going out to: {email_list}")
        
        templatefile = "email_reminder.html"
        html_message = render_to_string(templatefile)
        
        subject = "Pigskin Predictor: " + hours + " hour reminder"
        plaintextmessage = "This is your " + hours + " reminder to submit your predictions for week " + str(week)
        
        msg = EmailMultiAlternatives(subject = subject, body = plaintextmessage, from_email = "'Pigskin Predictor' <hello@pigskinpredictor.com>", to = ["'Pigskin Predictor Users' <hello@pigskinpredictor.com>"], bcc = email_list)
        msg.attach_alternative(html_message, "text/html")
        msg.send()

@shared_task
def save_results():
    resultsweek = PigskinConfig.objects.get(Name="live").ResultsWeek
    if int(resultsweek) > 18:
        pass
    else:
        if int(resultsweek) < 10:
            fileweek = '0'+str(resultsweek)
        else:
            fileweek = str(resultsweek)
        fileseason = str(PigskinConfig.objects.get(Name="live").PredictSeason)
        filename = 'data/resultsimport_'+fileseason+'_'+fileweek+'.json'
        bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')

        s3 = boto3.resource('s3')
        obj = s3.Object(bucket,filename)
        body = obj.get()['Body'].read().decode('utf-8')
        data = json.loads(body)

        # Check gamecount is correct before continuing
        resultscount = len(data)
        gamescount = Match.objects.filter(Season=PigskinConfig.objects.get(Name="live").PredictSeason, Week=int(resultsweek)).count()

        if resultscount != gamescount:
            sys.exit("Game count mismatch, aborting before scoring - please check import JSON file")

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
        for score in ScoresSeason.objects.filter(Season=PigskinConfig.objects.get(Name="live").PredictSeason):
            # Try / Except needed if a user misses a week
            try:
                weekscore = ScoresWeek.objects.get(Season=PigskinConfig.objects.get(Name="live").PredictSeason, User=score.User, Week=PigskinConfig.objects.get(Name="live").ResultsWeek)
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
                seasoncorrect = Prediction.objects.filter(PredSeason=PigskinConfig.objects.get(Name="live").PredictSeason, User=score.User, Points__gt=0).count()
                seasonpredcount = Prediction.objects.filter(PredSeason=PigskinConfig.objects.get(Name="live").PredictSeason, User=score.User).exclude(Points__isnull=True).count()
                score.SeasonPercentage = (seasoncorrect/seasonpredcount)*100
                # Recalculate Season Average
                score.SeasonAverage = score.SeasonScore/ScoresWeek.objects.filter(Season=PigskinConfig.objects.get(Name="live").PredictSeason, User=score.User).count()
                # Recalculate Banker Average
                banktotal = 0
                for banker in Prediction.objects.filter(PredSeason=PigskinConfig.objects.get(Name="live").PredictSeason, User=score.User, Banker=True):
                    if isinstance(banker.Points, int):
                        banktotal += banker.Points
                score.BankerAverage=banktotal/Prediction.objects.filter(PredSeason=PigskinConfig.objects.get(Name="live").PredictSeason, User=score.User, Banker=True).exclude(Points__isnull=True).count()
                score.save()

        # Update AllTime extended stats 
        for alltime in ScoresAllTime.objects.all():
            # Try / Except needed if a user misses a week
            try:
                weekscore = ScoresWeek.objects.get(Season=PigskinConfig.objects.get(Name="live").PredictSeason, User=alltime.User, Week=PigskinConfig.objects.get(Name="live").ResultsWeek)
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
        for i in ScoresSeason.objects.filter(Season=int(fileseason)):
            positiondict[i.User.pk]=scorecounter
            scorecounter += 1
        if int(resultsweek) == 1:
            for i in User.objects.all():
                # Append new season if previous data exists
                if i.Positions:
                    # Add new season
                    i.Positions['data'][str(fileseason)] = {}
                    try:
                        i.Positions['data'][str(fileseason)][str(resultsweek)] = positiondict[i.pk]
                    except(KeyError):
                        # Make position bottom of table if they didn't play in week 1
                        i.Positions['data'][str(fileseason)][str(resultsweek)] = usercount
                    i.save()
                # Create data object if none found
                else:
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
        for i in ScoresWeek.objects.filter(Season=PigskinConfig.objects.get(Name="live").PredictSeason, Week=PigskinConfig.objects.get(Name="live").ResultsWeek):
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

@shared_task
def get_livescores():
    # Will run at 5pm every week but only needs to run at 5pm one week of the year
    # when the UK clock changes go back in the last week of October (US goers back first Sunday of November)
    if dt.now().hour == 17:
        if not (dt.now().month == 10 and dt.now().day > 24):
            return
    for livegame in LiveGame.objects.all():
        try:
            url = f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={livegame.Game}"
            gamejson = requests.get(url).json()
            home = int(gamejson['header']['competitions'][0]['competitors'][0]['score'])
            away = int(gamejson['header']['competitions'][0]['competitors'][1]['score'])
            state = gamejson['header']['competitions'][0]['status']['type']['state']
            stateorder={'pre': 3, 'in': 1, 'post': 2}
            if livegame.HomeScore == home and livegame.AwayScore == away and livegame.State == stateorder[state]:
                # pre, in, post
                livegame.Updated = False
                livegame.save()
            else:
                livegame.HomeScore = home
                livegame.AwayScore = away
                livegame.State = stateorder[state]
                if home > away:
                    livegame.Winning = "Home"
                elif away > home:
                    livegame.Winning = "Away"
                else:
                    livegame.Winning = "Tie"
                livegame.Updated = True
                livegame.save()
        # Games will produce a KeyError for 'score' prior to kick-off
        except(KeyError):
            livegame.State = 3
            livegame.save()

# Task to run on Saturdays to wipe old live games and add tomorrow's game in prep for Sunday's live games
@shared_task
def populate_live():
    teamdict = {'ARI': 1, 'ATL': 2, 'BAL': 3, 'BUF': 4, 'CAR': 5, 'CHI': 6, 'CIN': 7, 'CLE': 8, 'DAL': 9, 'DEN': 10, 'DET': 11, 'GB': 12, 'HOU': 13, 'IND': 14, 'JAX': 15, 'KC': 16, 'LV': 17, 'LAC': 18, 'LAR': 19, 'MIA': 20, 'MIN': 21, 'NE': 22, 'NO': 23, 'NYG': 24, 'NYJ': 25, 'PHI': 26, 'PIT': 27, 'SF': 28, 'SEA': 29, 'TB': 30, 'TEN': 31, 'WSH': 32}
    for livegame in LiveGame.objects.all():
        livegame.delete()
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    # test for week 1
    # tomorrow = datetime.datetime.fromisoformat('2021-09-12').date()
    print("tomorrow is "+str(tomorrow))
    gamecount=0
    for game in Match.objects.filter(Season=PigskinConfig.objects.get(Name="live").PredictSeason):
        if game.DateTime.date() == tomorrow and game.DateTime.hour < 23:
            newlive = LiveGame(Game=game.GameID, HomeTeam=game.HomeTeam.ShortName, AwayTeam=game.AwayTeam.ShortName, KickOff=game.DateTime.strftime("%H%M"), TeamIndex=teamdict[game.AwayTeam.ShortName], State=3)
            newlive.save()
            gamecount += 1
    print(str(gamecount)+" live games imported")

# Version of above without date and time constraints to be used for testing pre-season so we can populate the live games table outside of the season
@shared_task
def populate_live_preseason_for_testing():
    teamdict = {'ARI': 1, 'ATL': 2, 'BAL': 3, 'BUF': 4, 'CAR': 5, 'CHI': 6, 'CIN': 7, 'CLE': 8, 'DAL': 9, 'DEN': 10, 'DET': 11, 'GB': 12, 'HOU': 13, 'IND': 14, 'JAX': 15, 'KC': 16, 'LV': 17, 'LAC': 18, 'LAR': 19, 'MIA': 20, 'MIN': 21, 'NE': 22, 'NO': 23, 'NYG': 24, 'NYJ': 25, 'PHI': 26, 'PIT': 27, 'SF': 28, 'SEA': 29, 'TB': 30, 'TEN': 31, 'WSH': 32}
    for livegame in LiveGame.objects.all():
        livegame.delete()
    gamecount=0
    for game in Match.objects.filter(Season=PigskinConfig.objects.get(Name="live").PredictSeason, Week=PigskinConfig.objects.get(Name="live").PredictWeek):
        newlive = LiveGame(Game=game.GameID, HomeTeam=game.HomeTeam.ShortName, AwayTeam=game.AwayTeam.ShortName, KickOff=game.DateTime.strftime("%H%M"), TeamIndex=teamdict[game.AwayTeam.ShortName], State=3)
        newlive.save()
        gamecount += 1
    print(str(gamecount)+" live games imported")

@shared_task
def fetch_results(fetchonly):
    week = PigskinConfig.objects.get(Name="live").ResultsWeek
    strweek = str(week)
    if int(week) > 18:
        pass
    else:
        season = PigskinConfig.objects.get(Name="live").PredictSeason
        strseason = str(season)
        path = "/temp_data/"

        if int(week) < 10:
            filename = "resultsimport_"+str(season)+"_0"+str(week)+".json"
        else:
            filename = "resultsimport_"+str(season)+"_"+str(week)+".json"
        
        pathandfile = path+filename

        outfile = open(pathandfile, "w")

        # Removed Thurs-Tues logic as below will produce a gameweek, no matter when it's requested
        source = f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={strseason}&week={strweek}"

        rawjson = requests.get(source).json()

        # Check to see if games have completed - sanity check in case it is run in week 1 before games have been played
        # Because registrations open a couple of weeks before, if the scheduled task is not disabled, the script will
        # Score all games as 0-0 without this check.  Address GitHub Issue #195.
        if rawjson['events'][0]['status']['type']['completed'] != True:
            sys.exit("Detected incomplete game on API - Please check gameweek and whether all games have completed")

        results = []

        for game in rawjson['events']:
            if game['status']['type']['completed'] != True:
                pass
            else:
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
                outerdict["pk"] = int(game['id'])
                outerdict["fields"] = innerdict
                results.append(outerdict)

        # Removed old WSH/WAS & LA/LAR Logic as 'new' teams with
        # corresponding PKs will be added from 2021 season

        sortedresults = sorted(results, key=lambda k: k['pk'])
        jsonout = json.dumps(sortedresults)
        outfile.write(jsonout)
        outfile.close()

        # Upload to S3
        bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        s3 = boto3.resource('s3')
        s3path = 'data/'+filename
        s3.Object(bucket, s3path).upload_file(Filename=pathandfile)
        
        if int(fetchonly) == 1:
            pass
        elif int(fetchonly) == 0:
            # Call Save Results once file is uploaded to S3
            # 30 second delay to let S3 sort itself out and ensure file is ready
            time.sleep(30)
            save_results()

@shared_task
# Configured to run in Celery config in settings.py on 1st April every year
def joker_reset():
    for user in User.objects.all():
        user.JokerUsed = None
        user.save()

# Weekly job to run every Wednesday night prior to PredictWeek increment to update game k/o times as some games are flexed later in the season
@shared_task
def kickoff_time_checker():
    # for game in Match.objects.filter(Season=PigskinConfig.objects.get(Name="live").PredictSeason, Week=int(os.environ['PREDICTWEEK'])+1):
    for game in Match.objects.filter(Season=PigskinConfig.objects.get(Name="live").PredictSeason, Week=(PigskinConfig.objects.get(Name="live").PredictWeek)+1):
        url = f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={game.GameID}"
        gamejson = requests.get(url).json()
        jsondatetime = gamejson['header']['competitions'][0]['date']
        game.DateTime = jsondatetime
        game.save()

# One Off job to run for current week
@shared_task
def kickoff_time_checker_current_week():
    for game in Match.objects.filter(Season=PigskinConfig.objects.get(Name="live").PredictSeason, Week=PigskinConfig.objects.get(Name="live").PredictWeek):
        url = f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={game.GameID}"
        gamejson = requests.get(url).json()
        jsondatetime = gamejson['header']['competitions'][0]['date']
        game.DateTime = jsondatetime
        game.save()

# Task to Update Predict/Results Week
@shared_task
def update_week(weektype):
    weektype = weektype.lower()

    match weektype:
        case "predict":
            currentweek = PigskinConfig.objects.get(Name="live").PredictWeek
        case "results":
            currentweek = PigskinConfig.objects.get(Name="live").ResultsWeek
        case _:
            sys.exit("Invalid week type argument provided - exiting.")
    
    print(f"Type was declared as {weektype}")
    
    print("Current week is "+str(currentweek))
    newweek = currentweek + 1
    print("Updating to " +str(newweek))
    
    config = PigskinConfig.objects.get(Name="live")
    match weektype:
        case "predict":
            config.PredictWeek += 1
            config.save()
        case "results":
            config.ResultsWeek += 1
            config.save()
    
    # We set various caches for Scoretables to speed-up loading performance
    # These have a TTL of 1 week so can sometimes persist past the Resultsweek increment
    # Clearing them down each week will ensure correct scoretable data is loaded
    if weektype == "results":
        for c in cachestoflush:
            cache.delete(c)
        print('Caches flushed')

# Task to Update Predict/Results Week
# UTC Check Version not currently in use
# Celery is configured as Europe/London
# So check functionality shouldn't be needed
@shared_task
def update_week_with_utc_check(weektype, utctime):
    timezonedbapikey = os.environ['TIMEZONEDBAPIKEY']
    weektype         = weektype.lower()

    match weektype:
        case "predict":
            varweek = "PredictWeek"
            correcttime = "21:00"
            currentweek = PigskinConfig.objects.get(Name="live").PredictWeek
        case "results":
            varweek = "ResultsWeek"
            correcttime = "08:00"
            currentweek = PigskinConfig.objects.get(Name="live").ResultsWeek
        case _:
            sys.exit("Invalid week type argument provided - exiting.")

    
    # UTC Checks
    # Script will be called at 8pm and 9pm (for predictweek deadline) & 7am and 8am (for resultsweek table updates) UTC by Cronjob
    # We want local time to always be 9PM/8AM
    # When local time is BST, 9pm BST is 8PM UTC
    # When local time is GMT, 9pm GMT is 9pm UTC
    changeondict = {
        'predict' : {
            20: 'BST',
            21: 'GMT'
            },
        'results': {
            7: 'BST',
            8: 'GMT'
            }
        }
    
    if not utctime in changeondict[weektype]:
        sys.exit("Incorrect UTC time provided - exiting.")

    
    print(f"Type was declared as {weektype}")
    
    # changeontz provides the string timezone that this invocation should increment on
    changeontz = changeondict[weektype][utctime]
    # Timezone Check
    apiparams = {"key" : timezonedbapikey, "by" : "zone", "zone" : "Europe/London", "format" : "json"}
    zonereq = requests.get(url="http://api.timezonedb.com/v2.1/get-time-zone", params=apiparams)
    discoveredtimezone = zonereq.json()['abbreviation']
    print(f"Discovered timezone is {discoveredtimezone}")
    print(f"This script was called at {utctime}:00 UTC")
    if discoveredtimezone == changeontz:
        print(f"Local Time in Europe/London is {correcttime} so incrementing {varweek} variable")
        increment = True
    else:
        print(f"Local Time in Europe/London is NOT {correcttime} so {varweek} variable will not increment")
        increment = False
        
    # Conditionally Update PredictWeek Env Var
    if increment:
        print("Current week is "+str(currentweek))
        newweek = currentweek + 1
        print("Updating to " +str(newweek))
        config = PigskinConfig.objects.get(Name="live")
        match weektype:
            case "predict":
                config.PredictWeek += 1
                config.save()
            case "results":
                config.ResultsWeek += 1
                config.save()

@shared_task
def disable_sunday_live():
    config = PigskinConfig.objects.get(Name="live")
    config.SundayLive = False
    config.save()

@shared_task
def enable_sunday_live():
    config = PigskinConfig.objects.get(Name="live")
    config.SundayLive = True
    config.save()
    
@shared_task
# Workaround for GitHub issue 243
def banker_flag_confirmation():
    config = PigskinConfig.objects.get(Name="live")
    week_to_check = config.PredictWeek - 1
    if week_to_check > 18:
        return
    season = config.PredictSeason
    bankers = Banker.objects.filter(BankWeek = week_to_check, BankSeason = season)
    countall = 0
    countchanged = 0
    badlist = []
    for banker in bankers:
        pred = Prediction.objects.get(User=banker.User, Game=banker.BankGame)
        if pred.Banker == False:
            pred.Banker = True
            pred.save()
            countchanged += 1
            badlist += str(pred)
        countall += 1
    print(f"Banker Flag Confirmation job complete. {countall} bankers checked, {countchanged} updated")
    if countchanged == 0:
        print("0 updated represents an error free week :)")
    else:
        logging.error("One or more banker Predictions were found without the banker flag")
        print("A repeat of GitHub issue 243 occured. See below offenders: -")
        for badpred in badlist:
            print(badpred)