from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
import pandas as pd
from decouple import config

API_KEY = config('EIA_API_KEY')


def get_mexico_pipeline_data():
    url = "http://api.eia.gov/series/?api_key={}&series_id=NG.N9132MX2.M".format(API_KEY)
    data = requests.get(url)
    graph_data = data.json()["series"][0]["data"]
    df = pd.DataFrame(graph_data, columns=['Date', 'Amount'])
    for index, row in df.iterrows():
        df.loc[index, "Date"] = datetime.strptime(df.loc[index, "Date"], "%Y%m")
        df.loc[index, "Amount"] = df.loc[index, "Amount"] / (30 * 1000)
    return df

def get_lng_data():
    url_truck = "http://api.eia.gov/series/?api_key={}&series_id=NG.NGM_EPG0_ETR_NUS-NMX_MMCF.M".format(API_KEY)
    url_vessel = "http://api.eia.gov/series/?api_key={}&series_id=NG.NGM_EPG0_EVE_NUS-NMX_MMCF.M".format(API_KEY)
    data_vessel = requests.get(url_vessel)
    data_truck = requests.get(url_truck)
    lng_vessel = data_vessel.json()["series"][0]["data"]
    lng_truck = data_truck.json()["series"][0]["data"]
    df_vessel = pd.DataFrame(lng_vessel, columns=['Date', 'Vessel Amount'])
    df_truck = pd.DataFrame(lng_truck, columns=['Date', 'Truck Amount'])
    for index, row in df_vessel.iterrows():
        df_vessel.loc[index, "Date"] = datetime.strptime(df_vessel.loc[index, "Date"], "%Y%m")
        df_vessel.loc[index, "Vessel Amount"] = df_vessel.loc[index, "Vessel Amount"] / (30 * 1000)
    for index, row in df_truck.iterrows():
        df_truck.loc[index, "Date"] = datetime.strptime(df_truck.loc[index, "Date"], "%Y%m")
        df_truck.loc[index, "Truck Amount"] = df_truck.loc[index, "Truck Amount"] / (30 * 1000)
    merged = pd.merge(df_truck, df_vessel, on='Date')
    merged["Total LNG"] = merged["Truck Amount"] + merged["Vessel Amount"]
    return merged

def build_export_mexico_chart():
    pipeline_data = get_mexico_pipeline_data()
    lng_data = get_lng_data()
    fig = plt.figure(figsize=(5.4*1.3, 4.3*1.3))
    ax = fig.gca()
    ax.grid(axis='y')
    ax.set_axisbelow(True)
    date_format = mdates.DateFormatter("%b-%y")
    ax.xaxis.set_major_formatter(date_format)
    plt.ylim(3, 6.5)
    plt.margins(x=0)
    plt.ylabel("NatGas Exports (Bcf/d)", weight="bold")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    plt.stackplot(pipeline_data["Date"][:37], pipeline_data["Amount"][:37], lng_data["Total LNG"][:37],
                  labels=["U.S. Pipeline Exports to Mexico", "U.S. LNG Exports to Mexico"],
                  colors=["navy", "deepskyblue"])
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left', ncol=2, mode="expand")
    plt.title("Monthly U.S. Natural Gas Exports to Mexico\nOct 2017-Oct 2020", y=1.15, weight="bold", fontdict={"size": 15})
    plt.subplots_adjust(top=.8, bottom=.15)

    plt.savefig("Mexico-Export-Chart.png", dpi=100)
    plt.show(dpi=100)

if __name__ == '__main__':
    build_export_mexico_chart()



