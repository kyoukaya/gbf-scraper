# granblue-scraper

Quick script thrown together to scrape and parse data from GW. Collects information from the top 80k individual ranking and individual guilds from a dictionary. Should take around 1.5 - 2 hrs to scrape the 80k rankings.
Also includes a script to append rank and honor data to memers in guilds.

## Installation

* Python 3.6
* The following packages:
  * selenium
  * seleniumrequests
  * pushbullet
  * pandas
* A *relatively* recent version of chrome/chromium
* Chrome webdriver

## Usage

* Point `OPTIONS.binary_location` to your chrome binary
* Fill up the pushbullet settings because you love pushbullet too
* Place the chrome webdriver executable in the root folder of the script
* Execute `granblue-scraper.py`, log in, and hit enter to continue the script once logged in
* ??? (your cookies might expire sometime inbetween)
* Hopefully you don't get banned for flooding
