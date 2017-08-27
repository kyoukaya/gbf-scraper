'''gbf-scraper v0.1 (27082017) by kyoukaya'''

import csv
from json import JSONDecodeError
from os import makedirs, path
from time import time as time_now
from time import sleep, strftime
import argparse
from sys import argv

from pushbullet import InvalidKeyError, Pushbullet
from seleniumrequests import Chrome

from config import config
from selenium import webdriver

GW_NUMBER = 32
CHROME_ARGUMENTS = '--disable-infobars'

LOG_FILE = '[{}]granblue-scraper.log'.format(strftime('%m-%d_%H%M'))


class Timer(object):
    '''Simple object to determine when we should refresh'''

    def __init__(self):
        self.start_time = time_now()

    def reset(self):
        self.start_time = time_now()

    def check_timeout(self, maxtime):
        if (time_now() - self.start_time) > maxtime:
            return True
        return False


def log(message):
    '''Prints to console and outputs to log file'''

    try:
        with open('.\\logs\\' + LOG_FILE, 'a',
                  encoding='utf-8', newline='') as fout:
            message = '[%s] %s' % (strftime('%a %H:%M:%S'), message)
            print(message)
            print(message, file=fout)
    except FileNotFoundError:
        makedirs('.\\logs')
        log('Created log folder')
        log(message)


def alert_operator(message, pause=True):
    '''Push alerts for CAPTCHAs, etc.'''
    if CFG.use_pb is True:
        try:
            pub = Pushbullet(CFG.api_key['PB'])
            push = pub.push_note('granblue-scraper', message)
            log(push)
        except InvalidKeyError:
            log('Invalid PB API key!')
    log(message)
    if pause:
        input('Press enter to continue...')


def csv_writer(rows, filename, write_rows=True):
    with open(filename, 'a', newline='', encoding='utf-8') as fout:
        writer = csv.writer(fout)
        if write_rows:
            writer.writerows(rows)
        else:
            writer.writerow(rows)


def parser(data, parse_type, **kwargs):
    rows = list()

    if parse_type == 'gw_individual':
        data = data['list']
        for k in data:
            k = data[k]
            rows.append((k['rank'], k['name'], k['total_defeat'],
                         k['contribution'], k['level'], k['user_id']))
        return rows

    elif parse_type == 'guild_members':
        data = data['list']
        for k in data:
            rows.append((k['name'], k['level'], k['member_position_name'],
                         k['id'], kwargs['faction_name'], kwargs['guild_name'],
                         kwargs['guild_id']))
        return rows

    elif parse_type == 'gw_guild':
        data = list(data['list'].items())
        for k in range(0, 10):
            try:
                pid = data[k][1]['id']
                name = data[k][1]['name']
                honors = data[k][1]['point']
                rank = data[k][1]['ranking']
                rows.append((rank, name, honors, pid))
            except IndexError:
                continue
        return rows

    elif parse_type == 'guild_ranks':
        data = data['list']
        for k in data:
            rows.append((k['level'],))
        return rows

    elif parse_type == 'guild_info':
        return data['guild_name'], data['guild_id']


def scraper(url, parse_type, **kwargs):
    headers = {
        'Accept': '''application/json'''
    }
    auth_check = True
    auth_timer = 0
    while True:
        if TIMER.check_timeout(60 * 30):
            GBF.refresh()
            TIMER.reset()
        try:
            response = GBF.request('get', url, headers=headers).json()
            rows = parser(response, parse_type, **kwargs)
            return rows
        except (ConnectionResetError, ConnectionError,
                ConnectionAbortedError, JSONDecodeError):
            if parse_type == 'guild_members':
                raise
            if (auth_timer - time_now() > 60) or auth_check:
                GBF.refresh()
                TIMER.reset()
                GBF.get('http://game.granbluefantasy.jp/#authentication')
                sleep(5)
                # Hard coded mobage login
                GBF.find_element_by_xpath('//*[@id="mobage-login"]/img').click()
                alert_operator('Reauthentication', pause=False)
                auth_timer = time_now()
                sleep(10)
            continue
        except:
            alert_operator('???', pause=False)


def handler(baseurl, parse_type, first, last, **kwargs):
    rows = list()
    guild_name = None
    guild_id = None
    if parse_type == 'guild_ranks':
        pass
    elif parse_type == 'guild_members':
        guild_info = scraper(
            f'http://game.granbluefantasy.jp/guild_other/guild_info/{baseurl}',
            'guild_info')
        log('Scraping {}'.format(guild_info[0]))
        guild_name = guild_info[0]
        guild_id = guild_info[1]
        baseurl = 'http://game.granbluefantasy.jp/guild_other/member_list/{}/{}'\
            .format({}, baseurl)

    for page in range(first, last + 1):
        log('Currently on page: {}'.format(page))
        rows.extend(scraper(baseurl.format(page), parse_type,
                            guild_name=guild_name,
                            guild_id=guild_id, **kwargs))
        if parse_type == 'gw_individual' or parse_type == 'gw_guild':
            csv_writer(rows, kwargs['filename'])
            rows = list()  # TODO unhackify

    if parse_type != 'gw_individual' or parse_type == 'gw_guild':
        return rows


def guild_members():
    factions = CFG.get_factions()
    directory = CFG.base_dir + '\\GW{}\\Guilds\\Information\\'.format(GW_NUMBER)
    filename = directory + '[{}]Guild Members.csv'.format(strftime('%m-%d_%H%M'))
    header = ('name', 'level', 'position', 'id', 'faction', 'guild', 'guild_id')
    guilds_scraped = list()
    makedirs(directory, exist_ok=True)
    csv_writer(header, filename, write_rows=False)
    for faction in factions:
        faction_name = faction[1]
        for guild in faction[0]:
            guild_id = faction[0][guild]
            try:
                rows = handler(guild_id, 'guild_members', 1, 3,
                               faction_name=faction_name)

                csv_writer(rows, filename)
                guilds_scraped.append((guild, faction_name, guild_id, 'public'))
            except Exception:
                guilds_scraped.append((guild, faction_name, guild_id, 'private'))
    csv_writer(guilds_scraped, directory + '[{}]guilds_scraped.csv'.format(
        strftime('%m-%d_%H%M')))


def gw_guild(first, last, seed_first, seed_last):
    baseurl = 'http://game.granbluefantasy.jp/teamraid0{}/ranking_guild/detail/{}'.format(
        GW_NUMBER, {})
    header = ('rank', 'name', 'battles', 'honor', 'id')
    directory = CFG.base_dir + '\\GW{}\\Guilds\\Ranking\\'.format(GW_NUMBER)
    filename = directory + '[{}]Preliminary_Guild_Rankings.csv'.format(
        strftime('%m-%d_%H%M'))
    makedirs(directory, exist_ok=True)

    # Prelims
    csv_writer(header, filename, write_rows=False)
    handler(baseurl, 'gw_guild', first, last, filename=filename)

    baseurl = 'http://game.granbluefantasy.jp/teamraid0{}/ranking_seedguild/detail/{}'.format(
        GW_NUMBER, {})
    filename = directory + '[{}]Seed_Guild_Rankings.csv'.format(strftime('%m-%d_%H%M'))

    # Seeds
    csv_writer(header, filename, write_rows=False)
    handler(baseurl, 'gw_guild', seed_first, seed_last, filename=filename)


def gw_individual(first, last):
    # headers = ('rank', 'name', 'battles', 'honor', 'level', 'id')
    directory = CFG.base_dir + '\\GW{}\\Individual\\'.format(GW_NUMBER)
    filename = (directory + '[{}]granblue-scraper_top80k({}-{}).csv'.format(
        strftime('%m-%d_%H%M'), first, last))
    url = 'http://game.granbluefantasy.jp/teamraid0{}/ranking_user/detail/{}'.format(
        GW_NUMBER, {})
    makedirs(directory, exist_ok=True)
    handler(url, 'gw_individual', first, last, filename=filename)


def guild_ranks(guild_id):
    url = 'http://game.granbluefantasy.jp/guild_other/member_list/{}/{}'
    filename = ('.\\guild_{}\\[{}]ranks.csv'.format(
        guild_id, strftime('%m-%d_%H%M')))
    makedirs('.\\{}'.format(guild_id), exist_ok=True)
    rows = handler(url.format({}, guild_id), 'guild_ranks', 1, 3)
    csv_writer(rows, filename)


def main():
    global GBF
    timestart = time_now()
    profile = path.abspath(".\\" + CFG.profile)

    parser = argparse.ArgumentParser(prog='gbf-scraper.py',
                                     description='A simple script for scraping various parts of Granblue Fantasy',
                                     usage='gbf-scraper.py [profile] [options]\nexample: python gbf-scraper.py profile2 -i 1 8000',
                                     formatter_class=argparse.MetavarTypeHelpFormatter)

    parser.add_argument('profile', nargs='?',
                        help='overwrites the default profile path', type=str)
    parser.add_argument('--individual', '-i', nargs=2,
                        help='scrapes GW individual rankings between the specified start and end', type=int)
    parser.add_argument('--guild', '-g', nargs=4,
                        help='scrapes GW guild rankings between the specified start and end prelim and seed pages', type=int)
    parser.add_argument('--members', '-m',
                        help='scrape member data from guilds specified in config.py', action='store_true')
    parser.add_argument('--info', '-n', help='scrapes rank info from a guild specified', type=int)
    parser.add_argument('--login', '-l',
                        help='pauses the script upon starting up to allow logging in', action='store_true')
    args = parser.parse_args()

    if len(argv) == 1:
        parser.print_help()
        quit()

    if args.profile is not None:
        log('Changing profile path to {}'.format(args.profile))
        profile = path.abspath('.\\' + args.profile)

    options = webdriver.ChromeOptions()
    log('Using profile at: {}'.format(profile))
    options.add_argument('user-data-dir=%s' % profile)
    for cargs in CHROME_ARGUMENTS.split():
        options.add_argument(cargs)
    GBF = Chrome(chrome_options=options)
    GBF.get('http://game.granbluefantasy.jp/#mypage')

    if args.login:
        log('Pausing to login')
        input('Press enter to continue...')

    if args.individual is not None:
        log('GW: {} Scraping individual rankings from page {} to page {}'.format(
            GW_NUMBER, *args.individual))
        gw_individual(*args.individual)
    if args.guild is not None:
        log('GW: {}\n Scraping prelim guild rankings from page {} to \
page {} and seed rankings from page {} to page {}'.format(
            GW_NUMBER, *args.guild))
        gw_guild(*args.guild)
    if args.info is not None:
        # TODO scrape more than just ranks?
        log('Scraping guild info for guild {}'.format(args.info))
        guild_ranks(args.info)
    if args.members:
        # DEFUNCT, used to be for EOP rankings
        log('Defunct -m flag')
        guild_members()

    alert_operator('Task finished. {} seconds elapsed.'.format(
        time_now() - timestart), pause=False)
    GBF.close()
    quit()


if __name__ == '__main__':
    TIMER = Timer()
    CFG = config()

    try:
        main()
    except Exception:
        GBF.close()
        alert_operator('exception occured', pause=False)
        raise
