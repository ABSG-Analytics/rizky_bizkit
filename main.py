logo = """
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                          ║
║                     #@.                                                                                  ║
║                    @&@@                                                                                  ║
║                   @(/%@@  ██████╗ ██╗███████╗██╗  ██╗██╗   ██╗   ██████╗ ██╗███████╗██╗  ██╗██╗████████╗ ║
║                  @@*& @&  ██╔══██╗██║╚══███╔╝██║ ██╔╝╚██╗ ██╔╝   ██╔══██╗██║╚══███╔╝██║ ██╔╝██║╚══██╔══╝ ║
║                 @&&* %@@  ██████╔╝██║  ███╔╝ █████╔╝  ╚████╔╝    ██████╔╝██║  ███╔╝ █████╔╝ ██║   ██║    ║
║               @@%((,/,@   ██╔══██╗██║ ███╔╝  ██╔═██╗   ╚██╔╝     ██╔══██╗██║ ███╔╝  ██╔═██╗ ██║   ██║    ║
║             ,&@*@&*/@@    ██║  ██║██║███████╗██║  ██╗   ██║█████╗██████╔╝██║███████╗██║  ██╗██║   ██║    ║
║           *&@&,/ *@@@     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝╚════╝╚═════╝ ╚═╝╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝    ║
║         (@@&@&&&*.@@/                                                                                    ║
║      %(@@%&&%%%@@&%#@%#  ,/*%@@@#,                               @@&@/%&@&%@&&&@                         ║
║  *&@@%&@@@((#%@@*//@@&%%%@@&&&@&&&@%&@@&&&&@#%@@##*             @&@@@ %&(/%,  @@@&@@@@@@@@%.             ║
║% *&&*@%@@@@@**#@%&(%(@%&@(&@,(,,.,...,.,.,,#,..*..,,*@         %&%@&**./%&&&&&&@@@#@@&@@@#&#@%#&@@@%%@&&@║
║@/&%#(%%@*#%&&.,@&%@&/&&&@@@&@@@@@%@@@@@@@@@@@#&&@/#%          #&@(,& /(&&& #&&&/(%@&&%%@&& &#@& &@@%#% *&║
║#&&##(&(/*,#% @@@&@&%%(@@%,,**#@&&&%#@&%*@@&&&%@@&(#&@@##     %&&(//&*(#&@  ./&.   ( # @ *%@@%*@/&#%/*@#&%║
║*/&&&&&%&@&&&/@@@%%#(#@&% ,,..&%,%,.,%,**@*#(&#%%&.          &#%//.&&/,.*% .@,(%,% # % # . ./  .,* %   (%*║
║@@@@@@@&&%&&@@%.#,,& / (& @@@@&@@#                          @%&/ , &/,*@(,./ ,##,((( . (** %,    , (.   %(║
║&#%/**@*.@,*,,,,**(%( ....&@%@&@&                           #&(*.&@# */@## /@@*,&&* . #(##@/*.@. /*&(/((##║
║&,....&,.*.. .*... ,.,....(#%                                &( &&@,&*&.% @/(@%%##@&%%@(*  #(&&&&@%#@@@&%@║
║@%@@@&#%%@%&@@@&(,.,,,,**.&@                                     &//.%&,& ,&%%&@(@&&@@@@%&&&&&@&@(        ║
║              *&@(#@.*%(#&                                          %%@&&&% &&@@&                         ║
║                                                                                                          ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

import requests
import io
from bs4 import BeautifulSoup
import xarray as xr
import pandas as pd
import numpy as np


def get_nwm_forcast() -> pd.DataFrame:
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
    df = xr.load_dataset(io.BytesIO(r.content), engine="h5netcdf").to_dataframe()
    df = df.reset_index(level=[0, 1])
    df = df.drop(
        [
            "crs",
            "nudge",
            "qSfcLatRunoff",
            "qBucket",
            "qBtmVertRunoff",
            "time",
            "reference_time",
        ],
        axis=1,
    )

    route_link_df = pd.read_csv("lat_lons.csv", index_col=0)
    df = pd.merge(df, route_link_df, left_index=True, right_index=True)

    return df


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
    print(logo)
    df = get_nwm_amomaly(prediction_length="long")
    print(df)
