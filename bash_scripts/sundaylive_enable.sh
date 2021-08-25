#! /bin/sh
# A script to increment the PREDICTWEEK variable on a weekly basis
curl -X PATCH https://api.heroku.com/apps/${PIGENV}/config-vars \
  -d '{
  "SUNDAYLIVE": "TRUE"
}' \
  -H "Content-Type: application/json" \
  -H "Accept: application/vnd.heroku+json; version=3" \
  -H "Authorization: Bearer $OAUTH"