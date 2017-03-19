import csv
from os import makedirs, path
from selenium import webdriver
from time import time as time_now
from time import sleep, strftime

from pushbullet import InvalidKeyError, Pushbullet
from seleniumrequests import Chrome

OPTIONS = webdriver.ChromeOptions()
PROFILE = path.abspath('.\\profile')
OPTIONS.add_argument('user-data-dir=%s' % PROFILE)
OPTIONS.binary_location = '.\\chrome-win32\\chrome.exe'

LOG_FILE = '[{}]GBFScraper.log'.format(strftime('%m-%d_%H%M'))
USE_PB = True
API_KEY = {
    'PB': 'o.LcYNI6OY3AHCI2mMBeNnKG9NFd7yk2LG',
}


def log(message):
    '''Prints to console and outputs to log file'''
    try:
        with open('.\\logs\\' + LOG_FILE, 'a', encoding='utf-8', newline='') as fout:
            message = '[%s] %s' % (strftime('%a %H:%M:%S'), message)
            print(message)
            fout.write(message + '\n')
    except FileNotFoundError:
        makedirs('.\\logs')
        log('Created log folder')
        log(message)


def alert_operator(message, pause=True):
    '''Push alerts for CAPTCHAs, etc.'''
    if USE_PB is True:
        try:
            pub = Pushbullet(API_KEY['PB'])
            push = pub.push_note('granblue-scraper', message)
            log(push)
        except InvalidKeyError:
            log('Invalid PB API key!')
    print(message)
    if pause:
        input('Press enter to continue...')


def csv_writer(row, filename):
    with open(filename, 'a', newline='', encoding='utf-8') as fout:
        writer = csv.writer(fout)
        writer.writerow(row)


def parser(d, parse_type, filename):
    if parse_type == "GW_individual":
        d = d['list']
        for k in d:
            k = d[k]
            row = (k['rank'], k['name'], k['total_defeat'],
                   k['contribution'], k['level'], k['user_id'])
            csv_writer(row, filename)
    elif parse_type == "guild_members":
        d = d['list']
        for k in d:
            row = (k['name'], k['level'], k['member_position_name'], k['id'])
            csv_writer(row, filename)


def scraper(url, filename, parse_type):
    headers = {
        'Accept': '''application/json'''
    }
    while True:
        try:
            r = GBF.request('get', url, headers=headers).json()
            parser(r, parse_type, filename)
            return
        # Doesn't seem to be catching timeouts?...
        except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
            alert_operator("Reauthentication required")
        log('Connection timed out')


def handler(baseurl, parse_type, filename, headers, first, last):
    csv_writer(headers, filename)
    for page in range(first, last + 1):
        log('Currently on page: {}'.format(page))
        scraper(baseurl.format(page), filename, parse_type)
        sleep(0.1)
    # csv_writer(('{} seconds elapsed'.format((time_now() - timestart_seconds)),), filename)


def guild_members():
    guilds = {
        'HSP': 147448,
        'Lum1': 388489,
        'Lum2': 401211,
        'Atelier': 418206,
        'Little Girls': 432330,
        'Falz Flag': 479206,
        'Haruna': 472465,
        'NoFlipCity': 518173,
        '(You)': 581111,
        'FOXHOUND': 590319,
        'TriadPrimus': 632242,
        'OppaiSuki': 678459,
        'Dem Bois': 705648,
        'COWFAGS': 841064,
        'Gransexual': 845439,
        'Bullies': 745085,
        'Aion no Me': 645927,
        'TOOT': 844716,
        'Fleet': 599992,
        'FMNL1': 540830,
        'FMNL2': 719518
    }
    directory = '.\\GW28\\Guilds\\Information\\'
    makedirs(directory, exist_ok=True)
    baseurl = 'http://game.granbluefantasy.jp/guild_other/member_list/{}/{}'
    for guild in guilds:
        log('Scraping {}'.format(guild))
        filename = directory + '[{}]{}.csv'.format(strftime('%m-%d_%H%M'), guild)
        headers = ('name', 'level', 'rank', 'id')
        handler(baseurl.format({}, guilds[guild]), 'guild_members', filename, headers, 1, 3)


def GW_individual(first, last):
    url = 'http://game.granbluefantasy.jp/teamraid028/ranking_user/detail/{}'
    headers = ('rank', 'name', 'battles', 'honor', 'level', 'id')
    filename = ('.\\GW28\\Individual\\[{}]granblue-scraper_top80k({}-{}).csv'.format(
        str((strftime('%m-%d_%H%M'))), first, last))
    makedirs('.\\GW28\\Individual\\', exist_ok=True)
    handler(url, 'GW_individual', filename, headers, first, last)


if __name__ == "__main__":
    GBF = Chrome(executable_path='.\\chromedriver.exe', chrome_options=OPTIONS)
    GBF.get('http://game.granbluefantasy.jp/#profile')
    input()
    timestart = time_now()
    try:
        GW_individual(4125, 8000)
        guild_members()
        alert_operator('Task finished. {} seconds elapsed.'.format(
            time_now() - timestart), pause=False)
        GBF.close()
        quit()
    except Exception:
        GBF.close()
        alert_operator('exception occured')
        raise
