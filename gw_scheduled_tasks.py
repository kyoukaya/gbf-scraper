'''Why implement threading when you can just open more instances!'''
import subprocess

import schedule

prefix = 'python granblue-scraper.py -i '


def job():
    subprocess.Popen(prefix + '1 2000')
    subprocess.Popen(prefix + '2001 4000 -p profile2')
    subprocess.Popen(prefix + '4001 6000 -p profile3')
    subprocess.Popen(prefix + '6001 8000 -p profile4')


schedule.every(interval=1).day.at('23:04').do(job)
