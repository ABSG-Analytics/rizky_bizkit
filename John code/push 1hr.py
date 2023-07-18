import requests
import io
from bs4 import BeautifulSoup
import xarray as xr
import pandas as pd
import numpy as np
def push_1hr_pred():   
    prediction_length = "short"
    base_url = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwm/post-processed/WMS/"
    if prediction_length == "short":
        base_url += "short_range/channel_rt/"
    elif prediction_length == "medium":
        base_url += "medium_range/channel_rt/"
    elif prediction_length == "long":
        base_url += "long_range/channel_rt/"
    else:
        raise Exception("not a vailed predicion length")

    # get the page with all the anomaly forcasts listed
    r = requests.get(base_url)
    soup = BeautifulSoup(r.text, "html.parser")

    # then take the most recent of those forcasts
    # in the contiguous US
    a_tags = soup.find_all("a")
    a_tags = list(map(lambda x: x.text, a_tags))
    a_tags = list(filter(lambda x: "channel_rt.conus.nc" in x, a_tags))
    data_url = base_url + a_tags[-1]
    r = requests.get(data_url)

    dataset = xr.load_dataset(io.BytesIO(r.content), engine="h5netcdf")
    flow_1hr = np.array(dataset.variables["streamflow"])[:,0]
    lat_lon_df = pd.read_csv("C:\\Users\\JWisniewski\\Downloads\\risky_bizkit-main\\risky_bizkit-main\\lat_lons.csv")
    if str(dataset['time'][0].data) not in lat_lon_df.columns: 
        lat_lon_df[str(dataset['time'][0].data)] = flow_1hr
    lat_lon_df.to_csv("C:\\Users\\JWisniewski\\Downloads\\risky_bizkit-main\\risky_bizkit-main\\lat_lons.csv")
    return
push_1hr_pred()
