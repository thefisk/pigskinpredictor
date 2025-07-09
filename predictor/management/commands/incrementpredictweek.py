import os, json, requests
from django.core.management.base import BaseCommand

# Below custom managament command added in Appliku migration
# Moved from ./predictor/apps.py because we need to run this
# AFTER the app has started in Appliku - this is triggered
# byy release.sh

class Command(BaseCommand):
    
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("utctime", type=int)
    
    def handle(self, *args, **kwargs):
        # Vars
        team             = os.environ['APPLIKUTEAM']
        id               = os.environ['APPLIKUAPPID']
        applikuapikey    = os.environ['APPLIKUAPIKEY']
        timezonedbapikey = os.environ['TIMEZONEDBAPIKEY']
        currentweek      = os.environ['PREDICTWEEK']
        utctime          = kwargs['utctime']
        
        # UTC Checks
        # Script will be called at both 8pm and 9pm UTC by Cronjob
        # We want local time to always be 9PM
        # When local time is BST, 9pm BST is 8PM UTC
        # When local time is GMT, 9pm GMT is 9pm UTC
        changeondict = {
            8: 'BST',
            9: 'GMT'
            }
        
        changeontz = changeondict[utctime]
        # Timezone Check
        apiparams = {"key" : timezonedbapikey, "by" : "zone", "zone" : "Europe/London", "format" : "json"}
        zonereq = requests.get(url="http://api.timezonedb.com/v2.1/get-time-zone", params=apiparams)
        discoveredtimezone = zonereq.json()['abbreviation']
        print(f"Discovered timezone is {discoveredtimezone}")
        print(f"This script was called at {utctime}PM UTC")
        if discoveredtimezone == changeontz:
            print("Local Time in Europe/London is 21:00 so incrementing PREDICTWEEK variable")
            increment = True
        else:
            print("Local Time in Europe/London is NOT 21:00 so PREDICTWEEK variable will not increment")
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
                if var['name'] == 'PREDICTWEEK':
                    weekobj = var
            weekobj['value'] = str(int(weekobj['value'])+1)
            envvars = { 'env_vars' : [ weekobj ] }
            print("Updating to " +weekobj['value'])
            data = json.dumps(envvars)
            update = requests.patch(url=url, headers=patchheaders, data=data)
            if update.status_code != 200:
                print(f"Error: {update.reason}")
            else:
                print(f"Successfully updated PREDICTWEEK to {weekobj['value']}")