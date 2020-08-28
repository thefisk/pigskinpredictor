# Pigskin Predictor
### *A weekly American Football predictions game*

#### Intro

This project is my first foray at making an actual functional web application, the site is chiefly a small project for personal development.

The site is a simple predictions game whereby people pick weekly match winners, including one road team banker, and score points based on the outcomes of the games.

It is based on the Django web framework and uses Javascript to select and post users' predictions via AJAX. The site is hosted on Heroku and makes use of Heroku scheduler tasks in conjunction with RunScript, part of django-extensions.

#### Application Flow

* The site uses three environment variables to track the season and weeks, RESULTSWEEK & PREDICTWEEK being independent from each other.

* The season's schedule is imported before the start of the season, maintaining original individual game keys as primary keys in the Match table.

* Users' select weekly winners, including their banker choice. Those selections are posted via AJAX to the Prediction and Banker models, with a link to the corresponding Match key.

* On a Tuesday morning three scripts are run via the Heroku scheduler: -
  * ~~The first pulls the results from an XML feed based on the current RESULTSWEEK env var and writes those to a JSON file with fields relevant to the Results model.~~
  * Following deprecation of the official, and free, XML feed, the first script now uses BeautifulSoup to scrape the results data from pro-football-reference.com. This isn't ideal as JSON/XML data is much easier to predict and manipulate, but I was unable to find a free API that I could pull results data from.  The script still outputs to a JSON file stored on AWS S3 ready to be imported by the application.
  * The second scripts reads that JSON file and imports the results into the Results database table
  * The third script increments the RESULTSWEEK env var
 
 * During the second script, as results are written to the Results table (again, matching a Match key), a Django save method override runs to find matching predictions in the Prediction table, and update those with relevant scores.
 
 * As Prediction scores are saved, a further save override methods adds the points to Weekly, Season, and All-Time Score tables.
 
 * Every Wednesday evening a further script is run to increment the PREDICTWEEK env var to make the next week's predictions available for selection.
 
 * The Leaderboard page pulls in season scores for each user, plus their score from the last week (based on RESULTSWEEK -1).
 
 * The Javascript for the predictions page has been written in a way to only allow road teams to be set as bankers, and to not allow previous bankers to be used.
