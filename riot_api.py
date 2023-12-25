from requests import get as requests_get
from yaml import safe_load

TEST_ENCRYPTED_SUMMONER_ID = "tD8zDdKSJkXTIu_8Waqg8hHoWYoez52Mn3jWanBfCduQziE"
TEST_ENCRYPTED_SUMMONER_PUUID = "vlfxFyHUFPF2k8nX6tD3APNKJUgEWfnQfvdkCEvF_sG4yP_D5edKnhDUlHWVuI7SZI8sO1QAxc_97Q"
TEST_MATCHES_IDS = (
    "EUW1_6287208553",
    "EUW1_6287028078",
    "EUW1_6286980106",
    "EUW1_6286937252",
    "EUW1_6286102724"
)

REGIONS = {
    "euw": {"platform": "euw1",
            "region": "europe"},
    "kr": {"platform": "kr",
            "region": "asia"},
    "eune": {"platform": "eun1",
                "region": "europe"},
    "na": {"platform": "na1",
            "region": "americas"},
    "br": {"platform": "br1",
            "region": "americas"},
    "jp": {"platform": "jp1",
            "region": "asia"},
    "lan": {"platform": "la1",
            "region": "americas"},
    "las": {"platform": "la2",
            "region": "americas"},
    "oce": {"platform": "oc1",
            "region": "americas"},
    "ru": {"platform": "ru",
            "region": "europe"},
    "tr": {"platform": "tr1",
            "region": "europe"},
}

RANKED_QUEUES = {
    "RANKED_SOLO_5x5": "Ranked Solo/Duo",
    "RANKED_FLEX_SR": "Ranked Flex",
    "RANKED_TFT_DOUBLE_UP": "TFT Double Up",
}

QUEUES = {
        0: "Custom",
        400: "Draft Pick",
        420: "Ranked Solo/Duo",
        430: "Blind Pick",
        440: "Ranked Flex",
        450: "ARAM",
        700: "Clash",
        830: "Coop vs AI Intro",
        840: "Coop vs AI Easy",
        850: "Coop vs AI Medium",
        900: "ARURF",
        1900: "URF"
}


class Summoner:
    """Class for storing summoner data"""
    def __init__(self, region, summoner_data, ranked_data):
        self._region = region
        self._summoner_data = summoner_data
        self._ranked_data = ranked_data

    @property
    def rank(self):
        res = {}
        for queue in self._ranked_data:
            if queue["queueType"] == "RANKED_SOLO_5x5":
                res["solo"] = RankedQueue(queue)
            elif queue["queueType"] == "RANKED_FLEX_SR":
                res["flex"] = RankedQueue(queue)
        return res

    @property
    def platform(self):
        return REGIONS[self._region]["platform"]

    @property
    def region(self):
        return REGIONS[self._region]["region"]

    @property
    def name(self):
        return self._summoner_data["name"]

    @property
    def level(self):
        return self._summoner_data["summonerLevel"]
    
    @property
    def icon(self):
        return RiotAPI.icon_url(self._summoner_data["profileIconId"])
    
    @property
    def summonerId(self):
        return self._summoner_data["id"]
    
    @property
    def puuid(self):
        return self._summoner_data["puuid"]

class RiotAPI:
    """Class for interacting with Riot API"""
    _api_key = None

    @classmethod
    def _load_api_key(cls):
        """Load API key from config file"""
        with open("config/config.yaml") as config:
            key = safe_load(config)["api_key"]
        cls._api_key = key
    
    @staticmethod
    def icon_url(icon_id):
        return f"https://ddragon.leagueoflegends.com/cdn/13.3.1/img/profileicon/{icon_id}.png"
    
    @staticmethod
    def match(match_id, region):
        """Get match data corresponding to match_id and region"""
        if not RiotAPI._api_key:
            RiotAPI._load_api_key()
        url = f"https://{REGIONS[region]['region']}.api.riotgames.com/lol/match/v5/" + \
              f"matches/{match_id}"
        headers = {"X-Riot-Token": RiotAPI._api_key}
        match_data = requests_get(url=url, headers=headers).json()
        return Match(match_data)
    
    @staticmethod
    def matchlist(puuid, region, start=0, count=10):
        """Get matchlist corresponding to puuid and region
        
        Return list of MatchStats objects
        """
        if not RiotAPI._api_key:
            RiotAPI._load_api_key()
        url = f"https://{REGIONS[region]['region']}.api.riotgames.com/lol/match/v5/" + \
              f"matches/by-puuid/{puuid}/ids?start={start}&count={count}"
        headers = {"X-Riot-Token": RiotAPI._api_key}
        matchlist_data = requests_get(url=url, headers=headers).json()
        return [RiotAPI.match(match, region).stats(puuid) for match in matchlist_data]
    
    @staticmethod
    def summoner(name, region):
        """Get summoner data corresponding to name and region
        
        Return Summoner object
        """
        if not RiotAPI._api_key:
            RiotAPI._load_api_key()
        headers = {"X-Riot-Token": RiotAPI._api_key}
        url = f"https://{REGIONS[region]['platform']}.api.riotgames.com/lol/summoner/v4/" + \
              f"summoners/by-name/{name}"
        summoner_data = requests_get(url=url, headers=headers).json()
        if "status" in summoner_data: return None
        url2 = f"https://{REGIONS[region]['platform']}.api.riotgames.com/lol/league/v4/" + \
               f"entries/by-summoner/{summoner_data['id']}"
        ranked_data = requests_get(url=url2, headers=headers).json()
        return Summoner(region, summoner_data, ranked_data)

    @classmethod
    def verify_api_key(cls):
        """Verify API key
        
        Return True if API key is valid, False otherwise
        """
        if not cls._api_key:
            cls._load_api_key()
        url = "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + \
              "Tryndamere"
        headers = {"X-Riot-Token": cls._api_key}
        res = requests_get(url=url, headers=headers)
        if res.status_code == 200:
            return True
        else:
            return False
    
    @staticmethod
    def champion_icon(champion_name):
        return f"https://ddragon.leagueoflegends.com/cdn/13.3.1/img/champion/{champion_name}.png"


class Match:
    """Class for storing match data"""
    def __init__(self, match_data):
        self._data = match_data


    def stats(self, summoner_puuid):
        for index, player in enumerate(self._data["info"]["participants"]):
            if player["puuid"] == summoner_puuid:
                return MatchStats(self._data["info"]["participants"][index], self._data["info"]["gameDuration"], self._data["info"]["queueId"])
    
    @property
    def duration(self):
        return self._data["gameDuration"]
    
    @property
    def game_mode(self):
        return QUEUES[self._data["queueId"]]
    
    @property
    def participants(self):
        return self._data["participants"]


class RankedQueue:
    """Class for storing ranked queue data"""
    def __init__(self, queue_data):
        self._data = queue_data
    
    @property
    def name(self):
        return RANKED_QUEUES[self._data["queueType"]]
    
    @property
    def rank(self):
        return f"{self._data['tier']} {self._data['rank']} ({self._data['leaguePoints']} LP)"

    @property
    def wins(self):
        return self._data["wins"]
    
    @property
    def losses(self):
        return self._data["losses"]
    
    @property
    def winrate(self):
        return round(self.wins / (self.wins + self.losses) * 100)

class MatchStats:
    """Class for storing match stats of a player"""
    def __init__(self, stats, duration, queue_id) -> None:
        self._stats = stats
        self._duration = duration
        self._queue_id = queue_id
    
    @property
    def stats(self):
        res = {
            "kills": self._stats["kills"],
            "deaths": self._stats["deaths"],
            "assists": self._stats["assists"],
            "cs": self._stats["totalMinionsKilled"],
            "gold": self._stats["goldEarned"],
            "vision": self._stats["visionScore"],
            "champion": self._stats["championName"],
            "champion_id": self._stats["championId"],
            "match_time": self._stats["timePlayed"],
            "win": self._stats["win"]
        }
        return res
    
    @property
    def champion_name(self):
        return self._stats["championName"]
    
    @property
    def level(self):
        return self._stats["champLevel"]
    
    @property
    def kills(self):
        return self._stats["kills"]
    
    @property
    def deaths(self):
        return self._stats["deaths"]
    
    @property
    def assists(self):
        return self._stats["assists"]
    
    @property
    def kda(self):
        return f"{self.kills}/{self.deaths}/{self.assists}"
    
    @property
    def cs(self):
        return self._stats["totalMinionsKilled"] + self._stats["neutralMinionsKilled"]
    
    @property
    def gold(self):
        return self._stats["goldEarned"]
    
    @property
    def vision(self):
        return self._stats["visionScore"]
    
    @property
    def champion_icon(self):
        return RiotAPI.champion_icon(self.champion_name)
    
    @property
    def match_time(self):
        return self._stats["timePlayed"]

    @property
    def result(self):
        if self._stats["win"]:
            return "Victory"
        else:
            return "Defeat"
    
    @property
    def win(self):
        return self._stats["win"]
    
    @property
    def duration(self):
        mins = self._duration // 60
        secs = self._duration % 60
        return f"{mins:02d}:{secs:02d}"
    
    @property
    def control_wards(self):
        return self._stats["visionWardsBoughtInGame"]
    
    @property
    def queue(self):
        return QUEUES[self._queue_id]