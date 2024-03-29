import requests
from datetime import datetime
import plotly.express as px
import pandas as pd


# Timestamp to date
def convert_timestamp_to_date(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')

# Civ Mapping (might change with new civs DLC)
civ_list = {
    1: "Aztecs", 2: "Bengalis", 3: "Berbers", 4: "Bohemians", 5: "Britons",
    6: "Bulgarians", 7: "Burgundians", 8: "Burmese", 9: "Byzantines", 10: "Celts",
    11: "Chinese", 12: "Cumans", 13: "Dravidians", 14: "Ethiopians", 15: "Franks",
    17: "Goths", 18: "Gurjaras", 19: "Huns", 20: "Incas", 21: "Indians",
    22: "Italians", 23: "Japanese", 24: "Khmer", 25: "Koreans", 26: "Lithuanians",
    27: "Magyars", 28: "Malay", 29: "Malians", 30: "Mayans", 31: "Mongols",
    32: "Persians", 33: "Poles", 34: "Portuguese", 36: "Saracens", 37: "Sicilians",
    38: "Slavs", 39: "Spanish", 40: "Tatars", 41: "Teutons", 42: "Turks",
    43: "Vietnamese", 44: "Vikings", 35: "Romans", 0: "Armenians", 16: "Georgians"
}

# API
BASE_URL = "https://aoe-api.reliclink.com/community/leaderboard/getRecentMatchHistory?title=age2&profile_names="
TIMEOUT = 10
USER_IDS_LIST = [
    {"id": 76561199195740571, "alias": "dicopatito"},
    {"id": 76561199207580572, "alias": "Carpincho"},
    {"id": 76561198191637438, "alias": "Nanox"},
    {"id": 76561198163778606, "alias": "Sir Monkey"}
]

pibes_data = []

# Iterate over user dictionaries and fetch data
for user_dict in USER_IDS_LIST:
    user_id = user_dict["id"]
    alias = user_dict["alias"]

    # Create URL for the current user
    user_url = f"{BASE_URL}[%22/steam/{user_id}%22]"

    # Get data
    response = requests.get(user_url, timeout=TIMEOUT)
    player_data = response.json()

    # Check if 'matchHistoryStats' key is present
    if 'matchHistoryStats' in player_data:
        # Process the matches
        matches = player_data['matchHistoryStats']

        profiles = player_data['profiles']
        profile_id_to_alias = {profile['profile_id']: profile['alias'] for profile in profiles}

        #Convert timestamp to date
        for match in matches:
            match['startgametime'] = convert_timestamp_to_date(match['startgametime'])

        # Extract player information
        player_info = []
        for match in matches:
            for member in match['matchhistorymember']:
                profile_id = member['profile_id']
                alias = profile_id_to_alias.get(profile_id, f"Unknown Alias for {profile_id}")
                player_info.append({
                    'alias': alias,
                    'name': member['profile_id'],
                    'civ': member['race_id'],
                    'elo': member['oldrating'],
                    'date': match['startgametime'],
                    'match_type': match['matchtype_id']
                })

        # Replace civ numbers with civ names
        for player in player_info:
            player['civ'] = civ_list.get(player['civ'], "Unknown")

        current_alias = user_dict["alias"]
        player_data = [entry for entry in player_info if entry['alias'] == current_alias]
        pibes_data.extend(player_data)

    else:
        print("No matches found for Steam ID")

filtered_data = [entry for entry in pibes_data if entry['match_type'] in [8, 9]]

#Convert to df
df = pd.DataFrame(filtered_data)

#Plotly Output
# Group data by alias and civ
grouped_data = df.groupby(['alias', 'civ']).size().reset_index(name='count')

# Create a pie chart for each alias
for alias in df['alias'].unique():
    alias_data = grouped_data[grouped_data['alias'] == alias]
    fig = px.pie(alias_data, names='civ', values='count', title=f'Civ Distribution for {alias} in 2024')
    fig.show()