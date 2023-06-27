logo = """
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                &@                                                                                                         ║
║                               #@.                                                                                                         ║
║                              @&@@          ██████╗ ██╗███████╗██╗  ██╗██╗   ██╗    ██████╗ ██╗███████╗██╗  ██╗██╗████████╗                ║
║                             @(/%@@         ██╔══██╗██║██╔════╝██║ ██╔╝╚██╗ ██╔╝    ██╔══██╗██║╚══███╔╝██║ ██╔╝██║╚══██╔══╝                ║
║                            @@*& @&         ██████╔╝██║███████╗█████╔╝  ╚████╔╝     ██████╔╝██║  ███╔╝ █████╔╝ ██║   ██║                   ║
║                           @&&* %@@         ██╔══██╗██║╚════██║██╔═██╗   ╚██╔╝      ██╔══██╗██║ ███╔╝  ██╔═██╗ ██║   ██║                   ║
║                         @@%((,/,@          ██║  ██║██║███████║██║  ██╗   ██║       ██████╔╝██║███████╗██║  ██╗██║   ██║                   ║
║                       ,&@*@&*/@@           ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝       ╚═════╝ ╚═╝╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝                   ║
║                     *&@&,/ *@@@                                                                                                           ║
║                   (@@&@&&&*.@@/                                                     & @,                                                  ║
║                %(@@%&&%%%@@&%#@%#     .(*,/*%@@@#,                                @@&@/%&@&%@&&&@                                         ║
║            *&@@%&@@@((#%@@*//@@&%%%%(@&&&@@&&&@&&&@%&@@&&&&@#%@@##*              @&@@@ %&(/%,  @@@&@@@@@@@@%.                             ║
║ &@%&%      *&&*@%@@@@@**#@%&(%(@%&@@@%&&,(&@,(,,.,...,.,.,,#,..*..,,*@          %&%@&**./%&&&&&&@@@#@@&@@@#&#@%#&@@@%%@&&@&#%#(&&&@@&@&%@ ║
║ @#@,@#/&#//&%#(%%@*#%&&.,@&%@&/&&&@@@@/%&@@&@@@@@%@@@@@@@@@@@#&&@/#%           #&@(,& /(&&& #&&&/(%@&&%%@&& &#@& &@@%#% *& &%  *(*%@@@@&& ║
║ &@@@#&@@@@&&##(&(/*,#% @@@&@&%%(@@%%&((,(,,**#@&&&%#@&%*@@&&&%@@&(#&@@##      %&&(//&*(#&@  ./&.   ( # @ *%@@%*@/&#%/*@#&%@&#&@@@@@@%%%@@ ║
║ ,@@#*&&&&#/&&&&&%&@&&&/@@@%%#(#@&%   ...(,,..&%,%,.,%,**@*#(&#%%&.           &#%//.&&/,.*% .@,(%,% # % # . ./  .,* %   (%*@@(,/##%##/##%& ║
║ ((@@@&@@@@@@@@@@&&%&&@@%.#,,& / (&  ,.@,@@@@@&@@#                           @%&/ , &/,*@(,./ ,##,((( . (** %,    , (.   %(.#.*((%%/&@#@@@ ║
║ &@&&&@@%&@#%/**@*.@,*,,,,**(%( ....    @*&@%@&@&                            #&(*.&@# */@## /@@*,&&* . #(##@/*.@. /*&(/((##@(,/,.//((#%&@/ ║
║ *@@@&@(**,,....&,.*.. .*... ,.,........,#(#%                                 &( &&@,&*&.% @/(@%%##@&%%@(*  #(&&&&@%#@@@&%@@%@/ .../(@@&(. ║
║ @#%%@@@%%&%@@@&#%%@%&@@@&(,.,,,,**.( .,&@&@                                      &//.%&,& ,&%%&@(@&&@@@@%&&&&&@&@(                   .    ║
║  /*  /@@@#             *&@(#@.*%(#&&%(.%                                            %%@&&&% &&@@&                                         ║
║                                                                                        @(                                                 ║
║                                                                                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

import math
import requests
import io
from bs4 import BeautifulSoup
import xarray as xr
import pandas as pd


def get_nwm_forcast():
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


def get_nwm_anomaly():
    base_url = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwm/post-processed/WMS/short_range/channel_rt/"

    # get the page with all the anomaly forcasts listed
    r = requests.get(base_url)
    soup = BeautifulSoup(r.text, "html.parser")

    # then take the most recent of those forcasts
    # in the contiguous US
    a_tags = soup.find_all("a")
    a_tags = list(map(lambda x: x.text, a_tags))
    a_tags = list(filter(lambda x: "conus" in x, a_tags))
    data_url = base_url + a_tags[-1]
    r = requests.get(data_url)

    # zip feature id and anomaly level then sort by feature id
    anomaly_dict = xr.load_dataset(io.BytesIO(r.content), engine="h5netcdf").to_dict()
    ids_and_anomalies = list(
        zip(
            anomaly_dict["coords"]["feature_id"]["data"],
            anomaly_dict["data_vars"]["streamflow_anomaly"]["data"],
        )
    )
    ids_and_anomalies.sort(key=lambda x: x[0])

    # get the max anomaly for each of these levels
    max_anomalies = []
    for _, anomalies in ids_and_anomalies:
        max_anomaly = max(anomalies)
        if math.isnan(max_anomaly):
            max_anomaly = 0.0
        max_anomalies.append(max_anomaly)

    # combine the anomalies with the lat lon df
    lat_lon_df = pd.read_csv("lat_lons.csv", index_col=0)
    lat_lon_df = lat_lon_df.sort_index()
    lat_lon_df["anomaly"] = max_anomalies

    return lat_lon_df


if __name__ == "__main__":
    print(logo)
    df = get_nwm_anomaly()

    print(df)
