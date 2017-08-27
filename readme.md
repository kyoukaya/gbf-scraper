# gbf-scrape

A couple of simple scripts thrown together to scrape and parse data from Granblue Fantasy's guild wars (GWs) and maybe other stuff too. Requests are not threaded but the script is easily instanced, `gw_scheduled_tasks.py`.

## Installation

* Python 3.6
* The following packages:
  * selenium
  * seleniumrequests
  * pushbullet
  * pandas (optional)
* A relatively recent version of chrome/chromium
* Chrome webdriver

## Usage

* Configure `config.py`
  * Set `use_pb` to true and enter your api key if you want pushes from pushbullet
* Place the chrome webdriver executable in the root folder of the script
* Run `python gbf-scrape.py -l` and login to your mobage account for initial profile setup

## Usage
`usage: gbf-scraper.py [profile] [options]`

`example: python gbf-scraper.py profile2 -i 1 8000`

|flag   |arguments|description|
|---------|---------|-----------|
|--individual, -i| start, end| Scrapes GW individual rankings between the specified start and end pages
|--guild, -g| prelim_start, prelim_end, seed_start, seed_end| Scrapes GW guild rankings between the specified start and end pages for both prelim and seed categories
|--members, -m|None|Scrape member data from guilds specified in `config.py`|
|--info, -i|guild_ID|Scrapes rank info from a guild specified|
|--login, -l|None|Pauses the script upon starting up to allow logging in|