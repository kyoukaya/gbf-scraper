import code
from os import makedirs, path
from random import uniform as random
from selenium import webdriver
from time import time as time_now
from time import sleep, strftime
import csv

from seleniumrequests import Chrome

OPTIONS = webdriver.ChromeOptions()
PROFILE = path.abspath('.\\profile')
OPTIONS.add_argument('user-data-dir=%s' % PROFILE)
OPTIONS.binary_location = '.\\chrome-win32\\chrome.exe'


def log(message):
    '''Prints to console and outputs to log file'''
    log_file = '[{}] GBFScraper.log'.format(strftime('%m-%d %H%M'))
    try:
        with open('.\\logs\\' + log_file, 'a', encoding='utf-8', newline='') as fout:
            message = '[%s] %s' % (strftime('%a %H:%M:%S'), message)
            print(message)
            fout.write(message + '\n')
    except FileNotFoundError:
        makedirs('.\\logs')
        log('Created log folder')
        log(message)


def csv_writer(row, filename):
    try:
        with open('.\\out\\' + filename, 'a', newline='', encoding='utf-8') as fout:
            writer = csv.writer(fout)
            writer.writerow(row)
    except FileNotFoundError:
        makedirs('.\\out')
        log('Created out folder')
        csv_writer(row, filename)


def scraper(url, filename):
    headers = {
        'Accept': '''application/json'''
    }
    r = GBF.request('get', url, headers=headers).json()['list']
    for k in r:
        row = (r[k]['rank'], r[k]['name'], r[k]['total_defeat'], r[
               k]['contribution'], r[k]['level'], r[k]['user_id'])
        csv_writer(row, filename)


def handler(baseurl, first, last):
    timestart_date = '{}'.format(strftime('%m-%d %H%M'))
    timestart_seconds = time_now()
    headers = ('rank', 'name', 'battles', 'honor', 'level', 'id')
    filename = ('[{}] GBFScraper ({} to {}).csv'.format(timestart_date, first, last))
    csv_writer(('Started at {} for pages {} to {}'.format(timestart_date, first, last),), filename)
    csv_writer(headers, filename)
    for page in range(first, last + 1):
        log('Currently on page: {}'.format(page))
        url = baseurl.format(page)
        scraper(url, filename)
        sleep(random(0.1, 1))
    csv_writer('Finished at {}. {} seconds elapsed'.format(
        strftime('%m-%d %H%M'), (time_now() - timestart_seconds)), filename)


if __name__ == "__main__":
    GBF = Chrome(executable_path='.\\chromedriver.exe', chrome_options=OPTIONS)
    GBF.get('http://game.granbluefantasy.jp/#profile')
    sleep(1)
    GBF.request('get', 'http://game.granbluefantasy.jp/#profile')
    try:
        dummy = input('press')
        url = 'http://game.granbluefantasy.jp/teamraid028/ranking_user/detail/{}'
        handler(url, 1, 8000)
    except Exception as exp:
        GBF.close()
        log(exp)
        raise
