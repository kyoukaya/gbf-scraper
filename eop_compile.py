import csv
import os
import time

import pandas

# Save CSVs to a zip for archival
ZIP = True
if ZIP:
    import zipfile


GW_NO = 33

ROOT_DIR = f'.\\GW{GW_NO}\\Guilds\\'
INV_DIR = f'.\\GW{GW_NO}\\Individual\\'
INF_DIR = ROOT_DIR + 'Information\\'
PRELIMS_CSV = INV_DIR + 'Prelims_80k.csv'
INTLUDE_CSV = INV_DIR + 'Top80k_Interlude.csv'
DAY1_CSV = INV_DIR + 'Finals_1_80k.csv'
DAY2_CSV = INV_DIR + 'Finals_2_80k.csv'
DAY3_CSV = INV_DIR + 'Finals_3_80k.csv'
DAY4_CSV = INV_DIR + 'Finals_4_80k.csv'
DAY5_CSV = INV_DIR + '[09-30_0023]GW33_finals5_80k_individuals.csv'


def get_last_modified(dir, contains=None):
    dir = os.path.abspath(dir) + '\\'
    files = list(map(lambda x: dir + x, os.listdir(dir)))
    if contains is not None:
        temp_files = list()
        for file in files:
            if contains.lower() in file.lower():
                temp_files.append(file)
        files = temp_files
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return files[0]


timestart = time.time()

members_csv = get_last_modified(INF_DIR, 'members')
guilds_csv = get_last_modified(INF_DIR, 'guilds_scraped')

# Read participants and their information with their ID as index
members_df = pandas.read_csv(members_csv, index_col=3)

# Read honors from ranking data with their ID as index
'''prelims_sr = pandas.read_csv(PRELIMS_CSV, index_col=5)['honor'].rename('prelims')
day1_sr = pandas.read_csv(DAY1_CSV, index_col=5)['honor'].rename('day_1')
day2_sr = pandas.read_csv(DAY2_CSV, index_col=5)['honor'].rename('day_2')
day3_sr = pandas.read_csv(DAY3_CSV, index_col=5)['honor'].rename('day_3')
day4_sr = pandas.read_csv(DAY4_CSV, index_col=5)['honor'].rename('day_4')'''

# We handle the final data differently, importing it as a DF with 2 colums instead of a series
final_df = pandas.read_csv(DAY5_CSV, index_col=5,).rename(
    columns={'honor': 'final_honors', 'rank': 'world_rank'})
# Clear out duplicate data before concatenating
final_df.drop(['name', 'level'], axis=1, inplace=True)

# Join it all together

'''result = pandas.concat((members_df, prelims_sr, day1_sr, day2_sr, day3_sr, day4_sr,
                        final_df), axis=1, join_axes=[members_df.index])'''

result = pandas.concat((members_df, final_df), axis=1,
                       join_axes=[members_df.index])

result.reset_index(inplace=True)

# Time to rank the guilds

guilds_df = pandas.read_csv(
    guilds_csv, names=['guild_alias', 'faction', 'id', 'paranoia'], header=None)

# Create columns for statistics
guilds_stats_columns = ('guild_members', 'percent_ranked', 'honors_sum',
                        'honors_mean', 'honors_median', 'honors_std',
                        'levels_mean', 'levels_median', 'levels_std')
for v in guilds_stats_columns:
    guilds_df[v] = None

guilds_df_public = guilds_df[guilds_df.paranoia == "public"]

# Not going to say this isn't a dirty hack but...
for enum, id in enumerate(guilds_df_public.id):
    guild = guilds_df[guilds_df.id == id]
    guild_df = result[result.guild_id == id]
    guild_members = guild_df.id.count()
    percent_ranked = guild_df.world_rank.count() / len(guild_df.world_rank)
    honors_mean = guild_df.final_honors.mean()
    honors_median = guild_df.final_honors.median()
    honors_sum = guild_df.final_honors.sum()
    honors_std = guild_df.final_honors.std()
    levels_mean = guild_df.level.mean()
    levels_median = guild_df.level.median()
    levels_std = guild_df.level.std()

    guild_stats_literal = (guild_members, percent_ranked, honors_sum,
                           honors_mean, honors_median, honors_std,
                           levels_mean, levels_median, levels_std)

    # Special case for using the scraped guild name instead of the one in cfg
    guilds_df.loc[
        guilds_df_public.index[enum], 'guild_name'] = guild_df.guild[guild_df.index[0]]

    for k, v in zip(guilds_stats_columns, guild_stats_literal):
        guilds_df.loc[
            guilds_df_public.index[enum], k] = v

# Calculate total GW stats
gw_total_stats_columns = ['honors_recorded', 'players',
                          'mean_honors', 'mean_player_level',
                          'guilds', 'guilds_public', 'guilds_percent_public']
gw_total_stats = pandas.DataFrame(index=[0, ], columns=gw_total_stats_columns)

gw_total_honors_recorded = result.final_honors.sum()
gw_total_players = result.id.count()
gw_total_mean_honors = gw_total_honors_recorded / gw_total_players
gw_total_mean_player_level = result.level.mean()
gw_total_guilds = guilds_df.id.count()
gw_total_guilds_public = guilds_df_public.id.count()
gw_total_guilds_percent_public = gw_total_guilds_public / gw_total_guilds

gw_total_stat_literals = (gw_total_honors_recorded, gw_total_players,
                          gw_total_mean_honors,
                          gw_total_mean_player_level, gw_total_guilds,
                          gw_total_guilds_public,
                          gw_total_guilds_percent_public)

for k, v in zip(gw_total_stats_columns, gw_total_stat_literals):
    gw_total_stats.loc[0, k] = v

gw_total_stats = gw_total_stats.transpose()

# Rearrange and sort columns
result = result[['world_rank', 'name', 'final_honors', 'battles',
                 'level', 'id', 'position', 'faction', 'guild', 'guild_id']]
result.sort_values('world_rank', inplace=True,)

guilds_df = guilds_df[['guild_name', 'guild_alias', 'honors_sum', 'id', 'faction', 'paranoia',
                       'guild_members', 'percent_ranked',
                       'honors_mean', 'honors_median', 'honors_std',
                       'levels_mean', 'levels_median', 'levels_std']]
guilds_df.sort_values('honors_sum', inplace=True, ascending=False)

# Output our data
os.makedirs(ROOT_DIR + f'Processed\\', exist_ok=True)

with pandas.ExcelWriter(ROOT_DIR +
                        f'Processed\\GW{GW_NO}_EOP_rankings.xlsx') as writer:
    gw_total_stats.to_excel(
        writer, index=True, header=False, sheet_name='GW Stats')
    guilds_df.to_excel(writer, index=False, sheet_name='Guild Rankings')
    result.to_excel(writer, index=False, sheet_name='Individual Rankings')

if ZIP:
    with zipfile.ZipFile(ROOT_DIR +
                         f'Processed\\GW{GW_NO}_EOP_rankings.csv.zip',
                         mode='w', compression=zipfile.ZIP_LZMA) as fout:
        fout.writestr(f'GW{GW_NO}_total_stats.csv',
                      gw_total_stats.to_csv(
                          index=True, header=False, encoding='utf-8'))
        fout.writestr(f'GW{GW_NO}_guild_ranks.csv',
                      guilds_df.to_csv(
                          index=False, encoding='utf-8'))
        fout.writestr(f'GW{GW_NO}_individual_ranks.csv',
                      result.to_csv(
                          index=False, float_format='%.0f', encoding='utf-8'))
else:
    gw_total_stats.to_csv(ROOT_DIR +
                          f'Processed\\GW{GW_NO}_total_stats.csv',
                          header=False, sep=':', encoding='utf-8')
    guilds_df.to_csv(ROOT_DIR +
                     f'Processed\\GW{GW_NO}_guild_rankings.csv',
                     index=False, encoding='utf-8')
    result.to_csv(ROOT_DIR +
                  f'Processed\\GW{GW_NO}_individual_ranks.csv',
                  index=False, float_format='%.0f', encoding='utf-8')


print('Operation took {} seconds'.format(time.time() - timestart))
