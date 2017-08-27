'''Appends rank and honor data to every guild in the Guilds/Information folder
by looking up the top 80k individual list with pandas'''
import csv
import time
from os import listdir, makedirs

import pandas

GW_NO = 32

root_dir = f'.\\GW{GW_NO}\\Guilds\\'
inv_dir = f'.\\GW{GW_NO}\\Individual\\'


def append_guilds():
    timestart = time.time()
    makedirs(root_dir + 'Processed\\', exist_ok=True)
    inv_ranking = inv_dir + sorted(listdir(inv_dir), reverse=True)[0]
    df = pandas.read_csv(inv_ranking)
    print('Using individual ranking file: {}'.format(sorted(listdir(inv_dir))))

    for filename in listdir(root_dir + 'Information\\'):
        fin = csv.reader(open(
            '''{}Information\\{}'''.format(root_dir, filename),
            mode='r', encoding='utf-8'))
        fout = csv.writer(open(
            '''{}Processed\\{}'''.format(root_dir, filename),
            mode='w', encoding='utf-8', newline=''))

        for line in fin:
            if line[3] != 'id':
                try:
                    player = df[df.id == int(line[3])]
                    rank = int(player['rank'])
                    honor = int(player['honor'])
                    line.insert(0, rank)
                    line.insert(0, honor)
                except TypeError:
                    line.insert(0, '')
                    line.insert(0, '')
            else:
                line.insert(0, 'rank')
                line.insert(0, 'honor')
            fout.writerow(line)

    print('Append operation took {} seconds'.format(time.time() - timestart))


if __name__ == "__main__":
    append_guilds()
