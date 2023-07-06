import time
import csv
import requests
import jsonlines
import os
from bs4 import BeautifulSoup
from typing import List, Tuple, Dict, Optional
from tqdm.auto import tqdm


class DanbooruArtistFinder:
    def __init__(self, jsonl_file):
        self.base_url = "https://danbooru.donmai.us"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }
        self.jsonl_file = jsonl_file
        if os.path.exists(jsonl_file):
            with jsonlines.open(jsonl_file, mode='r') as reader:
                self.found_artists = [obj['twitter_handle'] for obj in reader if not obj['not_found']]
        else:
            self.found_artists = []

    def _get_artist_tags(self, post_url: str) -> List[str]:
        response = requests.get(post_url)
        soup = BeautifulSoup(response.content, "html.parser")
        tags = soup.find_all("li", class_="tag-type-1")

        artists = []
        for tag in tags:
            artist_name = tag["data-tag-name"]
            artists.append(artist_name)

        return artists

    def get_twitter_handles_from_csv(self, csv_file):
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            reader.__next__()
            twitter_handles = [row[2] for row in reader]  # 'username'

        return twitter_handles

    def find_artists(self, twitter_handles: List[str]):
        with jsonlines.open(self.jsonl_file, mode='a') as writer:
            for handle in tqdm(twitter_handles, desc="Finding artists"):
                if handle in self.found_artists:
                    continue

                search_url = f"{self.base_url}/posts?tags=source%3Ahttps%3A%2F%2Ftwitter.com%2F{handle}"
                response = requests.get(search_url)
                soup = BeautifulSoup(response.content, "html.parser")
                post = soup.find("article", class_="post-preview")

                try:
                    if post:
                        post_id = post["data-id"]
                        post_url = f"{self.base_url}/posts/{post_id}"
                        artists = self._get_artist_tags(post_url)
                        writer.write({"twitter_handle": handle, "danbooru_key": artists, "not_found": False})
                        self.found_artists.append(handle)
                    else:
                        writer.write({"twitter_handle": handle, "danbooru_key": "", "not_found": True})
                        print(f"{handle}: not found")
                except Exception as e:
                    print(f"Exception occurred while processing handle '{handle}': {e}")

                time.sleep(2)


def run(csv_file, jsonl_file):
    finder = DanbooruArtistFinder(jsonl_file)
    twitter_handles = finder.get_twitter_handles_from_csv(csv_file)
    finder.find_artists(twitter_handles)


def run_from_list(artist_handle_list, jsonl_file):
    finder = DanbooruArtistFinder(jsonl_file)
    finder.find_artists(artist_handle_list)


import json


def get_handle_list():
    handle_file = "D:\CSC\sdxl-scrum\_data\g0ach_g0ach_following.json"
    with open(handle_file, 'r', encoding='utf-8') as f:
        handles = json.load(f)

    following = handles['g0ach']

    return following


if __name__ == '__main__':
    f_list = get_handle_list()
    run_from_list(f_list, 'results.jsonl')
