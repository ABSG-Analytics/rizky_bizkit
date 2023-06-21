import requests
import io
import datetime
from bs4 import BeautifulSoup
import xarray as xr
import pandas as pd


def get_nwm():
    base_url = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwm/prod/"
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d")

    date_url = base_url + "nwm." + date_str + "/short_range/"

    r = requests.get(date_url)
    soup = BeautifulSoup(r.text, "html.parser")
    a_tags = soup.find_all("a")
    data_urls = list(map(lambda x: x.text, a_tags[-72:]))
    data_urls = list(filter(lambda x: "channel" in x, data_urls))
    data_urls = list(filter(lambda x: "f001" in x, data_urls))

    r = requests.get(date_url + data_urls[0])
    nc = xr.load_dataset(io.BytesIO(r.content), engine="h5netcdf")
    df = nc.to_dataframe()
    df = df.drop(["crs", "nudge", "qSfcLatRunoff", "qBucket", "qBtmVertRunoff"], axis=1)
    print(df)


if __name__ == "__main__":
    get_nwm()
