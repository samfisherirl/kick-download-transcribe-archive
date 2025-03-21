from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
import re 
import time

class SeleniumFetcher:
    def __init__(self, binary_path, headless=True, window_size="1920x1080"):
        self.firefox_options = Options()

        if headless:
            self.firefox_options.add_argument("--headless")

        self.firefox_options.add_argument(f"--window-size={window_size}")
        self.firefox_options.binary_location = binary_path
        self.driver = None

    def fetch_page_content(self, url):
        try:
            service = FirefoxService(executable_path=GeckoDriverManager().install())
            self.driver = webdriver.Firefox(
                service=service, options=self.firefox_options
            )

            self.driver.get(url)
            time.sleep(5)
            page_content = self.driver.page_source
            return page_content  
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.quit_driver()

    def clean_text(self, text):
        # Updating pattern to capture all printable and typical control characters
        # from ASCII (32-126) plus newline (\n), carriage return (\r), and tab (\t)
        pattern = r"[^\x20-\x7E\r\n\t]"
        cleaned_text = re.sub(pattern, "", text)

        return cleaned_text

    def find_combined_video_urls(self, page_content, channel, base_url):
        # Ensure text is cleaned before processing
        page_content = self.clean_text(page_content)
        try:
            # Escape any special characters in the channel name
            channel_escaped = re.escape(channel)
            # Regex pattern to find all hrefs starting with '/escaped_channel/videos/'
            pattern = rf'href="(/{channel_escaped}/videos/[^"]+)"'
            matches = re.findall(pattern, page_content)
            # Combine matches with base_url
            combined_urls = [base_url + match for match in matches]
            return combined_urls  # Return list of full URLs
        except re.error as regex_error:
            print(f"Regex error: {regex_error}")
            return []
        except Exception as e:
            print(f"An error occurred during URL search: {e}")
            return []

    def quit_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"An error occurred during driver quit: {e}")
        self.driver = None


def run(channel='jstlk', firefox_binary_path=None, headless=True):
    if firefox_binary_path==None:
        firefox_binary_path = r"C:\Users\dower\Documents\FirefoxPortable\App\Firefox64\firefox.exe"
    page_url = f"https://kick.com/{channel}/videos"
    base_url = "https://kick.com"
    fetcher = SeleniumFetcher(binary_path=firefox_binary_path, headless=headless)
    content = fetcher.fetch_page_content(page_url)
    video_urls = fetcher.find_combined_video_urls(content, channel, base_url)
    print("Found Video URLs:")
    for video_url in video_urls:
        print(video_url)
    return video_urls

if __name__ == "__main__":
    binary_path = r"C:\Users\dower\Documents\FirefoxPortable\App\Firefox64\firefox.exe"
    run(binary_path)
