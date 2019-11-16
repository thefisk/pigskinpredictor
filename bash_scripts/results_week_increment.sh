#! /bin/sh
# A script to increment the RESULTSWEEK variable on a weekly basis
newweek="$(($RESULTSWEEK + 1))"
curl -X PATCH https://api.heroku.com/apps/pigskinpredictor/config-vars \
  -d '{
  "RESULTSWEEK": '"\"$newweek\""'
}' \
  -H "Content-Type: application/json" \
  -H "Accept: application/vnd.heroku+json; version=3" \
  -H "Authorization: Bearer $OAUTH"