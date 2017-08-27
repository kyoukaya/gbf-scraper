class config(object):
    """Simple object to store our config"""
    profile = 'profile'

    use_pb = False
    api_key = {
        'PB': '',
    }
    base_dir = '.'
    # RIP EOP ranking project ;_;
    factions_name = ['/gbfg/', 'GBF Intl./FB', 'NeoGAF', 'Reddit', 'Xieicord', '']
    
    gbfg = {
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
        'Fleet': 599992,  # Nice numbers
        'Chococats': 940560
    }
    facebook = {
        # From the FB spreadsheet
        # https://docs.google.com/spreadsheets/d/19B4TCcPp_Q3kP1ZGnPPKoNuVUsQU22C7tuMgmP83YoI/edit#gid=2019569367
        'FMNL1': 540830,
        'FMNL2': 719518,
        'HinaHana': 439238,
        'ClockTower': 588936,
        'Re Suzaku': 95896,
        'HeavenFall': 582522,
        'Sword of the Azure Sky': 394307,
        'LostRem': 583211,
        'Silver mop': 603737,
        'Casuals': 581533,
        'CasualToo': 940590,
        'UsappaFans': 593349,
        'ベルレフォーン': 629336,
        'Lazulis': 608395,
        'WAFURU': 580596,
        'Cirque': 585483,
        'SOS団': 264977,  # Anon submitted
        'Frost Shiva': 512489,
        'Capybaras': 758757,
        'Tasty Bytes': 796108,
        'Policecrew': 605525,
        'GG': 652875,  # Unsure about this one
        'Sugoi-loli': 608367,
        'Unknown': 719387,
        'Innova': 537992,
        'Jiogurt': 722695,
        'Gensokyo': 633574,
        'Genesis': 623655,
        'Waifus': 273172,
        'Skyfall': 733589,
        'KusoGaijin': 585025,
        'Roundabout': 387190,
        'Virasexual': 583647
    }
    neogaf = {
        # Anon submitted
        'GAFantasy': 569957,
        'GAFCypher': 526010
    }
    reddit = {
        # Obtained through the pinned messages on the discord #friend_and_crew channel
        'Skysea': 587804,  # Anon submitted
        'Phalanx': 581814,
        'Excelsior': 877812,
        'Veritas': 635031,
        'スカイ★フェスタ': 825209,
        'Acuris': 621654,
        'SwagSquad': 604822,
        'Arcadia': 590673,
        'Fafnir': 676156,
        'Einherjar': 836022,
        'Seraphs': 604919,
        'Freelancer': 584799,
        'Moogles': 637448,
        'Avaris': 812709,
        'Eientei': 748646,
        'NextGen': 580436,
        'Simplicity': 583879,
        'Wednesday': 559155,
        'Abyssos': 531849,
        'Callisto': 580822,
        'VapeNation': 580098
    }
    xieicord = {
        # From #pinboard
        'HSP': 147448,
        'Brilliance': 541495,
        'Radiance': 462254,
        'Nausea': 703905,
        'Candescence': 590514,
        'Diligence': 592343,
        'Kings': 552744,
        'Ariadust': 940664,
        'Gravity': 394016
    }
    no_faction = {
        # Guilds that don't belong in other factions
        'DOKKAN★': 581203,  # Falz Flag's sister guild that got bullied off /gbfg/
        '四季': 946943,
        'Ferrifags': 656403
    }

    factions_literal = (gbfg, facebook, neogaf, reddit, xieicord, no_faction)

    def get_factions(self):
        faction_list = list(zip(self.factions_literal, self.factions_name))
        return faction_list

    def count_guilds(self):
        counter = 0
        for faction in self.factions_literal:
            counter += len(faction)
        return counter
