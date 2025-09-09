from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
import numpy as np

##################################
# Global statistics of dataframes
##################################

def print_stats(df):
    num_rows = len(df)
    num_unique_transmitters = df["transmitterId"].nunique()
    num_unique_receivers = df["receiverId"].nunique()
    min_time = df["timestamp"].min()
    max_time = df["timestamp"].max()

    print(f"Nombre de lignes : {num_rows}")
    print(f"Nombre d'émetteurs uniques : {num_unique_transmitters}")
    print(f"Nombre de récepteurs uniques : {num_unique_receivers}")
    print(f"Date/heure min : {min_time}")
    print(f"Date/heure max : {max_time}")

def print_stats_small(df):
    num_rows = len(df)
    num_unique_transmitters = df["transmitterId"].nunique()
    num_unique_receivers = df["receiverId"].nunique()
    print(f"Nb. de lignes/émetteurs/récepteurs : {num_rows:>8} {num_unique_transmitters:>8} {num_unique_receivers:>8}")

##################################
# Plotting functions
##################################

def plot_metrics_multi(mydf):
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 8))
    ax1, ax2, ax3, ax4 = axes.flatten()

    for name, df in mydf.items():
        # 1) nb_counts
        y, bins = np.histogram(df["nb_counts"], bins=25)
        ax1.plot(bins[:-1], y, label=name)
        ax1.set_xlim(0, 200) 
        
        # 2) time_window
        y, bins = np.histogram(df[["transmitterId","time_window"]].drop_duplicates()["time_window"]/60, bins=25)
        ax2.plot(bins[:-1], y, label=name)

        # 3) max_rssi
        y, bins = np.histogram(df[["transmitterId","max_rssi"]].drop_duplicates()["max_rssi"], bins=20)
        ax3.plot(bins[:-1], y, label=name)

        # 4) digit_2 (categorical)
        counts = df["digit_2"].value_counts()
        ax4.bar(counts.index, counts.values, alpha=0.5, label=name)

    for ax, title in zip(
        [ax1, ax2, ax3, ax4],
        ["Nombre de mesures par émetteur",
        "Fenêtre de présence (minutes)",
        "Max RSSI par émetteur",
        "Distribution de digit_2"]
    ):
        ax.set_title(title)
        ax.set_yscale("log")
        ax.set_ylabel("Nombre d'émetteurs")
        ax.legend(fontsize=8)

    fig.tight_layout()
    plt.show()


def plot_metrics(df):
        
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 8))
    ax1, ax2, ax3, ax4 = axes.flatten()

    ax1.hist(df["nb_counts"], bins=50, color="#87CEFA")
    ax1.set_title("Nombre de mesures par émetteur")
    ax1.set_ylabel("Nombre d'émetteurs")
    ax1.set_yscale("log")

    ax2.hist(df[["transmitterId", "time_window"]].drop_duplicates()["time_window"]/60, bins=50, color="#FFA07A")
    ax2.set_title("Fenêtre de présence (minutes)")
    ax2.set_ylabel("Nombre d'émetteurs")
    ax2.set_yscale("log")

    ax3.hist(df[["transmitterId", "max_rssi"]].drop_duplicates()["max_rssi"], bins=50, color="#90EE90")
    ax3.set_title("Max RSSI par émetteur")
    ax3.set_ylabel("Nombre d'émetteurs")
    ax3.set_yscale("log")

    ax4.hist(df["digit_2"], bins=50, color="#D8BFD8")
    ax4.set_title("Nombre de mesures par émetteur")
    ax4.set_ylabel("Nombre d'émetteurs")

    plt.figure(figsize=(8, 5))
    plt.hexbin(
        df[["transmitterId", "time_window"]].drop_duplicates()["time_window"]/60,
        df[["transmitterId", "max_rssi"]].drop_duplicates()["max_rssi"],
        gridsize=50,  # number of hexagons, adjust for resolution
        cmap="viridis",  # pleasant colormap
        norm=mcolors.LogNorm()  # log scale for density
    )
    plt.colorbar(label="Density")
    plt.xlabel("Time window (minutes)")
    plt.ylabel("Max RSSI")
    plt.title("Max RSSI vs fenêtre de présence (minutes)")
    plt.show()


def wrangle_data(df):
    
    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%b %d, %Y @ %H:%M:%S.%f")

    # Ensure RSSI is integer
    df["rssi"] = df["rssi"].astype(int)

    # Ensure IDs are strings
    df["transmitterId"] = df["transmitterId"].astype(str)
    df["receiverId"] = df["receiverId"].astype(str)

    return df


def build_metrics(df):

    # Number of measurements per transmitter
    print("Calculating number of measurements per transmitter...")
    df_metrics = (
        df["transmitterId"]
        .value_counts()
        .reset_index()
        .rename(columns={"count": "nb_counts"})
    )
    df = df.merge(df_metrics, on="transmitterId", how="left")
    del df_metrics

    # Calculate max-min time for each transmitter
    print("Calculating time window and max RSSI per transmitter...")    
    df_metrics = (
        df.groupby("transmitterId")
        .agg(
          min_time=("timestamp", "min"),
          max_time=("timestamp", "max"),
          max_rssi=("rssi", "max")
        )
      .reset_index()
    )
    df_metrics["time_window"] = (df_metrics["max_time"] - df_metrics["min_time"]).dt.total_seconds()
    df = df.merge(df_metrics[["transmitterId", "time_window", "max_rssi"]], on="transmitterId", how="left")
    del df_metrics

    # Second character in the mac address
    print("Extracting second character of transmitterId...")
    unique_ids = df["transmitterId"].unique().tolist()
    #print(unique_ids[ :10])
    #chars_used = sorted(set(''.join(unique_ids)))
    #print(chars_used[ :10])
    df_metrics = pd.DataFrame(
        [list(uid) for uid in unique_ids], 
        columns=[f"char_{i}" for i in range(len(unique_ids[0]))]
    )
    df_metrics = df_metrics[["char_1"]]
    df_metrics = df_metrics.rename(columns={"char_1": "digit_2"})
    df_metrics["transmitterId"] = unique_ids
    del unique_ids
    df = df.merge(df_metrics, on="transmitterId", how="left")
    del df_metrics

    return df

def read_data(data_link):
    #print(data_link)
    if not Path(data_link).is_file():
        raise FileNotFoundError(f"File not found: {data_link}")
    df = pd.read_csv(data_link)
    return df
