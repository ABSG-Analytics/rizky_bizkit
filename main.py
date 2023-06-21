import requests
import datetime
from bs4 import BeautifulSoup


def get_nwm(timeframe="short"):
    base_url = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwm/prod/"
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d")

    date_url = base_url + "nwm." + date_str
    # TODO investigate long vs med vs short
    # notice 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwm/prod'

    total_url = date_url + "/short_range/"

    r = requests.get(total_url)
    soup = BeautifulSoup(r.text, "html.parser")
    a_tags = soup.find_all("a")
    data_urls = list(map(lambda x: x.text, a_tags[len(a_tags) - 72 :]))

    for data_url in data_urls:
        fname = "netCDF/" + data_url
        r = requests.get(total_url + data_url)
        with open(fname, "wb") as f:
            f.write(r.content)

        break


if __name__ == "__main__":
    get_nwm()
