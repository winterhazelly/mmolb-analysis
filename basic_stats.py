import hashlib
import json
from pathlib import Path

import requests

MY_TEAM_ID = "68060831b57069886d0df010"
HTTP_CACHE_DIR = Path("http_cache")

def stable_str_hash(in_val: str) -> str:
    return hex(int(hashlib.md5(in_val.encode("utf-8")).hexdigest(), 16))[2:]

def get_json(url: str) -> dict:
    HTTP_CACHE_DIR.mkdir(exist_ok=True)

    cache = {}
    cache_file_path = HTTP_CACHE_DIR / f"{stable_str_hash(url)}.json"
    try:
        with open(cache_file_path) as cache_file:
            cache = json.load(cache_file)
    except FileNotFoundError:
        pass

    if url in cache:
        return cache[url]

    data = requests.get(url).json()
    cache[url] = data
    with open(cache_file_path, "w") as cache_file:
        json.dump(cache, cache_file)

    return data

def main():
    team_obj = get_json(f"https://mmolb.com/api/team/{MY_TEAM_ID}")

    for player in team_obj["Players"]:
        player_obj = get_json(f"https://mmolb.com/api/player/{player['PlayerID']}")

        # if not player_obj["Stats"]:
        #     print("No stats for ", player["FirstName"], player["LastName"])

        for stats_obj in player_obj["Stats"].values():
            try:
                ip = stats_obj["batters_faced"] / 3
                era = 9 * stats_obj["earned_runs"] / ip

                # Innings pitched has a special display format in baseball
                ip_whole = int(ip)
                ip_remainder = int((ip - ip_whole) / 3 * 10)
                if ip_remainder == 0:
                    ip_str = f"{ip_whole}"
                else:
                    ip_str = f"{ip_whole}.{ip_remainder}"
                era_str = f"ERA {era:.2f} ({ip_str} IP)"
            except KeyError:
                era_str = None

            if era_str is not None:
                print(player["Position"], player["FirstName"], player["LastName"], era_str)


if __name__ == '__main__':
    main()
