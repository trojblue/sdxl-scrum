import os
import signal
import atexit
import dotenv
from Scweet.user import get_users_following
from Scweet.const import load_env_variable
from Scweet.utils import init_driver

class SimplifiedInfoRetriever:
    def __init__(self, env_path: str = ".env", headless: bool = True):
        self.env_path = env_path
        self.headless = headless
        self.driver = None
        self._load_env_variables()

        signal.signal(signal.SIGINT, self._handle_exit)
        atexit.register(self._handle_exit)

    def _load_env_variables(self):
        self.env = dotenv.load_dotenv(self.env_path, verbose=True)
        self.user_data_dir = load_env_variable("DRIVER_USER_DATA_DIR", none_allowed=True)

        if not os.path.exists(self.user_data_dir):
            os.makedirs(self.user_data_dir)

    def _handle_exit(self):
        print("Program terminating. ...")
        if self.driver:
            self.driver.quit()

    def _get_chrome_options_str(self) -> str:
        """
        Chrome options:
        - user agent
        - user data dir
        """
        UA = "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        user_data_dir = "--user-data-dir=" + self.user_data_dir
        allow_data_saver = "--allow-insecure-localhost --allow-running-insecure-content --disable-web-security " \
                           "--disable-features=IsolateOrigins,site-per-filter"
        allow_storage = "--disable-web-security --allow-running-insecure-content"

        options_list = [UA, user_data_dir, allow_data_saver, allow_storage]

        return " ".join(options_list)

    def init_webdriver(self):
        options = self._get_chrome_options_str()
        self.driver = init_driver(headless=self.headless, option=options)

    def get_users_following(self, users_list: list[str], verbose: int = 0, wait: int = 2, limit: int = float('inf')):
        following = get_users_following(
            users=users_list,
            env=self.env_path,
            headless=self.headless,
            verbose=verbose,
            wait=wait,
            limit=limit,
            # existing_driver=self.driver,
            # login=False,
            # add_at_sign=False,
        )
        return following

if __name__ == '__main__':
    retriever = SimplifiedInfoRetriever()
    retriever.init_webdriver()
    following = retriever.get_users_following(['@trojblue'])
    print(following)