import csv
import time
from os import listdir, makedirs
import code
import pandas

GW_NO = 30

root_dir = f'.\\GW{GW_NO}\\Guilds\\'
inv_dir = f'.\\GW{GW_NO}\\Individual\\'
filename = '{}Information\\[05-26_2027]Guild Members.csv'.format(root_dir)
inv_ranking = inv_dir + sorted(listdir(inv_dir), reverse=True)[0]
prelims_dir = inv_dir + 'Prelims_80k.csv'
interlude_dir = inv_dir + 'Top80k_Interlude.csv'
day1_dir = inv_dir + 'Finals_1_80k.csv'
day2_dir = inv_dir + 'Finals_2_80k.csv'
day3_dir = inv_dir + 'Finals_3_80k.csv'
day4_dir = inv_dir + 'Finals_4_80k.csv'
day5_dir = inv_dir + 'Finals_5_80k.csv'

timestart = time.time()

# Read participants and their information with their ID as index
members_df = pandas.read_csv(filename, index_col=3)

# Read honors from ranking data with their ID as index
prelims_sr = pandas.read_csv(prelims_dir, index_col=5)['honor'].rename('prelims')
day1_sr = pandas.read_csv(day1_dir, index_col=5)['honor'].rename('day_1')
day2_sr = pandas.read_csv(day2_dir, index_col=5)['honor'].rename('day_2')
day3_sr = pandas.read_csv(day3_dir, index_col=5)['honor'].rename('day_3')
day4_sr = pandas.read_csv(day4_dir, index_col=5)['honor'].rename('day_4')

# We handle the final data differently, importing it as a DF with 2 colums instead of a series
final_df = pandas.read_csv(day5_dir, index_col=5).rename(columns={'honor': 'final', 'rank': 'world_rank'})
# Clear out duplicate data before concatenating
final_df.drop(['name', 'level'], axis=1, inplace=True)

# Join it all together
result = pandas.concat((members_df, prelims_sr, day1_sr, day2_sr, day3_sr, day4_sr,
                        final_df), axis=1, join_axes=[members_df.index])

result.reset_index(inplace=True)

# Rearrange columns
result = result[['world_rank', 'final', 'battles', 'name', 'level', 'id', 'position', 'faction',
                 'guild', 'guild_id', 'prelims', 'day_1', 'day_2', 'day_3', 'day_4']]

result.sort_values('world_rank', inplace=True, kind='mergesort')

result.reset_index(inplace=True, drop=True)

with pandas.ExcelWriter('test_ownscrape.xlsx') as writer:
    result.to_excel(writer, sheet_name='Rankings')

print('Append operation took {} seconds'.format(time.time() - timestart))
