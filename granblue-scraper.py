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
USE_PB = False
API_KEY = {
    'PB': '',
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


def csv_writer(rows, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as fout:
        writer = csv.writer(fout)
        writer.writerows(rows)


def parser(data, parse_type, filename):
    rows = list()
    if parse_type == 'gw_individual':
        rows.append('rank', 'name', 'battles', 'honor', 'level', 'id')  # Headers
        data = data['list']
        for k in data:
            k = data[k]
            rows.append(k['rank'], k['name'], k['total_defeat'],
                        k['contribution'], k['level'], k['user_id'])
    elif parse_type == 'guild_members':
        rows.append('name', 'level', 'rank', 'id')  # Headers
        data = data['list']
        for k in data:
            rows.append(k['name'], k['level'], k['member_position_name'], k['id'])
    csv_writer(rows, filename)


def scraper(url, filename, parse_type):
    headers = {
        'Accept': '''application/json'''
    }
    while True:
        try:
            response = GBF.request('get', url, headers=headers).json()
            parser(response, parse_type, filename)
            return
        # Doesn't seem to be catching timeouts?...
        except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
            alert_operator('Reauthentication required')


def handler(baseurl, parse_type, filename, first, last):
    for page in range(first, last + 1):
        log('Currently on page: {}'.format(page))
        scraper(baseurl.format(page), filename, parse_type)
        sleep(0.1)


def guild_members():
    guilds = {
        # /gbfg/
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
        # ???
        'FMNL1': 540830,
        'FMNL2': 719518,
        # Discord
        'HinaHana': 439238,
        # Reddit
        'TestGuildPleaseIgnore': 0000,
        # Facebook
        'SEANiggers': 696969
    }
    directory = '.\\GW28\\Guilds\\Information\\'
    makedirs(directory, exist_ok=True)
    baseurl = 'http://game.granbluefantasy.jp/guild_other/member_list/{}/{}'
    for guild in guilds:
        log('Scraping {}'.format(guild))
        filename = directory + '[{}]{}.csv'.format(strftime('%m-%d_%H%M'), guild)
        handler(baseurl.format({}, guilds[guild]), 'guild_members', filename, 1, 3)


def gw_individual(first, last):
    url = 'http://game.granbluefantasy.jp/teamraid028/ranking_user/detail/{}'
    filename = ('.\\GW28\\Individual\\[{}]granblue-scraper_top80k({}-{}).csv'.format(
        str((strftime('%m-%d_%H%M'))), first, last))
    makedirs('.\\GW28\\Individual\\', exist_ok=True)
    handler(url, 'gw_individual', filename, first, last)


if __name__ == '__main__':
    GBF = Chrome(chrome_options=OPTIONS)
    GBF.get('http://game.granbluefantasy.jp/#profile')
    input()
    TIMESTART = time_now()
    try:
        gw_individual(1, 8000)
        guild_members()
        alert_operator('Task finished. {} seconds elapsed.'.format(
            time_now() - TIMESTART), pause=False)
        GBF.close()
        quit()
    except Exception:
        GBF.close()
        alert_operator('exception occured')
        raise
