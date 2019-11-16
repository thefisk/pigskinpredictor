#! /bin/sh
# A script to increment the PREDICTWEEK variable on a weekly basis
newweek="$(($PREDICTWEEK + 1))"
curl -n -X PATCH https://api.heroku.com/apps/pigskinpredictor/config-vars \
  -d '{
  "PREDICTWEEK": '"\"$newweek\""'
}' \
  -H "Content-Type: application/json" \
  -H "Accept: application/vnd.heroku+json; version=3"