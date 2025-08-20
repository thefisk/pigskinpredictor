import os, json, requests, sys
from django.core.management.base import BaseCommand

# Below custom management command added in Appliku migration
# Moved from ./predictor/apps.py because we need to run this
# AFTER the app has started in Appliku - this is triggered
# by release.sh

# should be invoked by 'python manage.py updateweek predict 20' etc
# the above would be the invocation command to run at 8pm utc for the PREDICTWEEK variable

class Command(BaseCommand):
    
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("weektype", type=str)
        parser.add_argument("utctime", type=int)
    
    def handle(self, *args, **kwargs):
        # Vars
        team             = os.environ['APPLIKUTEAM']
        id               = os.environ['APPLIKUAPPID']
        applikuapikey    = os.environ['APPLIKUAPIKEY']
        timezonedbapikey = os.environ['TIMEZONEDBAPIKEY']
        utctime          = kwargs['utctime']
        weektype         = kwargs['weektype'].lower()

        match weektype:
            case "predict":
                varweek = "PREDICTWEEK"
                correcttime = "21:00"
            case "results":
                varweek = "RESULTSWEEK"
                correcttime = "08:00"
            case _:
                sys.exit("Invalid week type argument provided - exiting.")

        currentweek      = os.environ[varweek]
        
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
            getheaders = {'accept': 'application/json', 'authorization': f"Token {applikuapikey}"}
            patchheaders = {'content-type': 'application/json', 'authorization': f"Token {applikuapikey}"}
            url=f"https://api.appliku.com/api/team/{team}/applications/{id}/config-vars"
            r = requests.get(url = url, headers=getheaders)
            print("Current week is "+currentweek)
            body = r.json()
            for var in body['env_vars']:
                if var['name'] == varweek:
                    weekobj = var
            weekobj['value'] = str(int(weekobj['value'])+1)
            envvars = { 'env_vars' : [ weekobj ] }
            print("Updating to " +weekobj['value'])
            data = json.dumps(envvars)
            update = requests.patch(url=url, headers=patchheaders, data=data)
            if update.status_code != 200:
                print(f"Error: {update.reason}")
            else:
                print(f"Successfully updated {varweek} to {weekobj['value']}")