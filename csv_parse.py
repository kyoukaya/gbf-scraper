import csv
CSV_PATH = 'guilds.csv'


class guild(object):
    def __init__(self, id, guild_alias, faction, comments):
        self.guild_alias = guild_alias
        self.faction = faction
        self.id = id
        self.comments = comments

    def __repr__(self):
        repr = 'Alias: {}\nID: {}\nFaction: {}\nComment: {}'.format(
            self.guild_alias, self.id, self.faction, self.comments)
        return repr


def duplicate_check(guilds):
    duplicates = set()
    ids = list()

    # List all the guild IDs
    for guild in guilds:
        ids.append(guild.id)

    # List dedup routine from JohnLaRooy
    # https://stackoverflow.com/questions/9835762/find-and-list-duplicates-in-a-list
    seen = set()
    seen_add = seen.add
    # adds all elements it doesn't know yet to seen and all other to seen_twice
    seen_twice = set(x for x in guilds if x in seen or seen_add(x))
    # turn the set into a list (as requested)
    
    # Raise exception if there are any duplicates
    if seen_twice != set():
        raise Exception(duplicates)


def csv_parse():
    guilds_list = list()
    with open(CSV_PATH, newline='', encoding='utf-8') as csv_in:
        reader = csv.reader(csv_in)
        reader.__next__()  # Skip header row
        for row_num, row in enumerate(reader):
            try:
                guilds_list.append(guild(*row))
            except:
                print('Error occured while parsing row {}'.format(row_num))
    duplicate_check(guilds_list)
    return guilds_list


if __name__ == '__main__':
    import time
    time_start = time.time()
    guilds_list = csv_parse()
    time_end = time.time()
    print('Time elapsed: {}s\nGuilds parsed: {}'.format(
        time_end - time_start, len(guilds_list)))
