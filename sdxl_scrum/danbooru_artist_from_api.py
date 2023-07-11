import time
import requests
import jsonlines
import tempfile

import base64
from getpass import getpass


class DanbooruArtistFinder:
    def __init__(self):
        self.base_url = "https://danbooru.donmai.us"
        self.jsonl_file = tempfile.NamedTemporaryFile(delete=False).name
        self.found_artists = []
        self.username = "trojblue"
        self.api_key = "GxxdkUzfJhdr5btsiCcLbMNT"

    def find_artists(self, url: str):
        with jsonlines.open(self.jsonl_file, mode='a') as writer:
            if url in self.found_artists:
                return self.found_artists

            auth_str = f"{self.username}:{self.api_key}"
            auth_b64 = base64.b64encode(auth_str.encode()).decode()

            headers = {
                "Authorization": f"Basic {auth_b64}"
            }

            search_url = f"{self.base_url}/posts.json?tags=source%3A{url}&limit=1"
            response = requests.get(search_url, headers=headers)
            print("TEXT", response, response.status_code)
            data = response.json()

            print(data)

            if len(data) > 0:
                post = data[0]
                tags = post["tag_string_artist"].split(" ")
                writer.write({"url_handle": url, "danbooru_key": tags, "not_found": False})
                self.found_artists.append(url)
            else:
                writer.write({"url_handle": url, "danbooru_key": "", "not_found": True})
                print(f"{url}: not found")

            time.sleep(2)
            return self.found_artists


def local_test(url):
    finder = DanbooruArtistFinder()
    artists = finder.find_artists(url)
    return artists


if __name__ == "__main__":
    url = "https://twitter.com/miya_ki00"  # replace with the url you want to test with
    print(local_test(url))
