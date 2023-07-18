import requests
import io
from bs4 import BeautifulSoup
import xarray as xr
import pandas as pd
import numpy as np
import json
import os
from logo import LOGO

DATA_DIR = "data"
VELO_AVG_PATH = os.path.join(DATA_DIR, "velocities_avg.npy")
STRM_AVG_PATH = os.path.join(DATA_DIR, "strm_flows_avg.npy")
DATA_PTS_PATH = os.path.join(DATA_DIR, "data.json")


def one_hour_forcast():
    base_url = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwm/prod/"
    r = requests.get(base_url)

    soup = BeautifulSoup(r.text, "html.parser")
    short_range_url = base_url + soup.find_all("a")[-1].text + "short_range/"

    r = requests.get(short_range_url)
    soup = BeautifulSoup(r.text, "html.parser")

    a_tags = soup.find_all("a")
    a_tags = list(map(lambda x: x.text, a_tags))
    a_tags = list(filter(lambda x: "channel" in x and "f001" in x, a_tags))

    data_url = short_range_url + a_tags[-1]
    r = requests.get(data_url)
    dataset = xr.load_dataset(io.BytesIO(r.content), engine="h5netcdf")
    velocities = np.array(dataset.variables["velocity"])
    strm_flows = np.array(dataset.variables["streamflow"])

    if velocities.shape != (2776738,):
        raise Exception(f"velocities shape is {velocities.shape}, not (2776738,)")
    if strm_flows.shape != (2776738,):
        raise Exception(f"strm_flows shape is {strm_flows.shape}, not (2776738,)")

    return velocities, strm_flows


def reavg_data(velo_arr: np.ndarray, strm_arr: np.ndarray):
    with open(DATA_PTS_PATH, "r+") as f:
        data = json.load(f)

        num_data_pts = data["num_data_pts"] + 1
        new_weight = 1.0 / num_data_pts
        old_weight = 1.0 - new_weight
        data["num_data_pts"] = num_data_pts

        f.seek(0)
        f.truncate()
        json.dump(data, f)

    with open(VELO_AVG_PATH, "r+b") as f:
        velo_avg = np.load(f)

        velo_arr[np.isnan(velo_arr)] = velo_avg[np.isnan(velo_arr)]
        velo_avg[np.isnan(velo_avg)] = velo_arr[np.isnan(velo_avg)]

        new_velocities_avg = np.average(
            np.vstack((velo_avg, velo_arr)),
            axis=0,
            weights=[old_weight, new_weight],
        )

        f.seek(0)
        f.truncate()
        np.save(f, new_velocities_avg, allow_pickle=True, fix_imports=False)

    with open(STRM_AVG_PATH, "r+b") as f:
        strm_avg = np.load(f)

        strm_arr[np.isnan(strm_arr)] = strm_avg[np.isnan(strm_arr)]
        strm_avg[np.isnan(strm_avg)] = strm_arr[np.isnan(strm_avg)]

        new_strm_flows_avg = np.average(
            np.vstack((strm_avg, strm_arr)),
            axis=0,
            weights=[old_weight, new_weight],
        )

        f.seek(0)
        f.truncate()
        np.save(f, new_strm_flows_avg, allow_pickle=True, fix_imports=False)


def get_nwm_amomaly(prediction_length="short") -> pd.DataFrame:
    # set the url based on requested prediction length
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

    max_anomaly = np.array(dataset.variables["streamflow_anomaly"]).max(
        axis=1, initial=0
    )
    feature_id = np.array(dataset.variables["feature_id"])
    anomaly_df = pd.DataFrame(
        max_anomaly, columns=["streamflow_anomaly"], index=feature_id
    )
    lat_lon_df = pd.read_csv("lat_lons.csv", index_col=0)

    df = pd.merge(
        lat_lon_df, anomaly_df, left_on="feature_id", right_index=True, how="inner"
    )
    df = df.fillna(0)

    return df


if __name__ == "__main__":
    print(LOGO)

    velo_arr, strm_arr = one_hour_forcast()
    # with open(VELO_AVG_PATH, "wb") as f:
    #     np.save(f, velo_arr, allow_pickle=True, fix_imports=False)
    # with open(STRM_AVG_PATH, "wb") as f:
    #     np.save(f, strm_arr, allow_pickle=True, fix_imports=False)
    reavg_data(velo_arr, strm_arr)
