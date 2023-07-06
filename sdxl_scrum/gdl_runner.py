import subprocess
from tqdm.auto import tqdm
import csv
import datetime
from typing import Optional
from unibox import UniLogger


class GdlRunner:
    def __init__(
            self, url_template:str, check_interval_days: int = 3, dst_dir: Optional[str] = None, logger: Optional[UniLogger] = None
    ):
        """

        :param url_template: eg.  "https://twitter.com/{}/media"
        :param check_interval_days:
        :param dst_dir:
        :param logger:
        """
        self.check_interval = datetime.timedelta(days=check_interval_days)
        self.dst_dir = dst_dir
        self.logger = logger or UniLogger("gallery_dl")
        self.url_template = "https://twitter.com/{}/media"  if not url_template else url_template

        # filters: python语法, 变量名见和图片一起保存的json
        self.filters = {
            # "width": ">= 512",
            # "height": ">= 512",
            "image_width": ">= 512",
            "image_height": ">= 512",
            "extension": "not in ('mp4', 'gif')",
            # "date": "> datetime(2019, 1, 1)",
            # "favorite_count": "> 20",
        }

    @staticmethod
    def read_handles(file_path: str) -> list:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines()]

    def run_gallery_dl(self, handle: str, dst_dir: Optional[str] = None):
        url = self.url_template.format(handle)
        flags = "--mtime-from-date --write-metadata --write-info-json"

        # Format filters into a command string
        filter_command = " and ".join(f"{k} {v}" for k, v in self.filters.items())
        filter_command = f'--filter "{filter_command}"'

        # Combine everything into the final command
        command = f"gallery-dl {url} {flags} {filter_command}"

        if dst_dir and not self.dst_dir:
            command += f" --dest {dst_dir}"
        else:
            command += f" --dest {self.dst_dir}"

        self.logger.info("gallery-dl: running command: " + command)

        # Run gallery-dl
        subprocess.run(command, shell=True)

        self.logger.info(f"gallery-dl: finished for {handle}")

    def check_and_update_csv(self, txt_path: str, csv_path: str = None):
        if csv_path is None:
            csv_path = txt_path.replace(".txt", ".csv")

        # Initialize last_checked as empty dictionary
        last_checked = {}

        # Try to read the csv file to get the last checked times
        try:
            with open(csv_path, "r") as csvfile:
                reader = csv.DictReader(csvfile)
                # Populate last_checked only if csv file read is successful
                last_checked = {
                    row["handle"]: datetime.datetime.strptime(row["last_checked"], "%Y-%m-%d %H:%M:%S.%f")
                    for row in reader
                }
        except FileNotFoundError:
            # If the csv file does not exist, create it with headers
            with open(csv_path, "w") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["handle", "last_checked"])  # Write column names

        # Read the handles from the txt file
        handles = self.read_handles(txt_path)
        progress_bar = tqdm(handles, unit="user")
        now = datetime.datetime.now()

        for handle in progress_bar:
            last_checked_time = last_checked.get(handle)
            if last_checked_time is None or now - last_checked_time > self.check_interval:
                progress_bar.set_description(f"Downloading media for {handle}")
                self.run_gallery_dl(handle, self.dst_dir)
                last_checked[handle] = now

                # Update the CSV every 5 minutes
                if (datetime.datetime.now() - now).total_seconds() > 5 * 60:
                    print("Updating CSV...")
                    self.update_csv(csv_path, last_checked)
                    now = datetime.datetime.now()

        # Save the final state
        self.update_csv(csv_path, last_checked)

    @staticmethod
    def update_csv(csv_path: str, last_checked: dict):
        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)

            # Write column names
            writer.writerow(["handle", "last_checked"])

            for handle, checked_time in last_checked.items():
                writer.writerow([handle, checked_time])


if __name__ == "__main__":
    file_path = "D:\CSC\sdxl-scrum\_data\\found_danbooru_keys.txt"
    demo_download_dir = r"O:\gallery-dl"
    url_template = "\"https://danbooru.donmai.us/posts?tags={}\""
    downloader = GdlRunner(url_template, dst_dir = demo_download_dir)
    downloader.check_and_update_csv(txt_path=file_path)
