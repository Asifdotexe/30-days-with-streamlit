"""
Day 4 out of 30
Building a YouTube dashboard using the following data
link: https://www.kaggle.com/datasets/kenjee/ken-jee-youtube-data

@author: Asif Sayyed
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime

# loading the aggregated metric by video dataset
aggregated_metric_by_video = pd.read_csv(
    "data/ken-jee-yt-data/Aggregated_Metrics_By_Video.csv"
)
# skipping the first row and including everything else
aggregated_metric_by_video = aggregated_metric_by_video.iloc[1:,:]

# loading aggregated metric by country and subscriber status dataset
aggregated_metric_by_subs = pd.read_csv(
    "data/ken-jee-yt-data/Aggregated_Metrics_By_Country_And_Subscriber_Status.csv"
)

# loading the comment and time series dataset
comment_data = pd.read_csv("data/ken-jee-yt-data/All_Comments_Final.csv")
time_series_data = pd.read_csv("data/ken-jee-yt-data/Video_Performance_Over_Time.csv")

# performing cleaning and feature engineering on aggregated metric by video dataset
# updating the colum names
aggregated_metric_by_video.columns = ['Video','Video title',
                                      'Video publish time','Comments added',
                                      'Shares','Dislikes','Likes',
                                      'Subscribers lost','Subscribers gained',
                                      'RPM (USD)','CPM (USD)', 'Average % viewed',
                                      'Average view duration', 'Views',
                                      'Watch time (hours)','Subscribers',
                                      'Your estimated revenue (USD)',
                                      'Impressions', 'Impressions CTR(%)']

# updating the datatypes
aggregated_metric_by_video['Video publish time'] = pd.to_datetime(
    aggregated_metric_by_video['Video publish time'],
    # since the dateformat is %b %m, %y using mixed format to infer it
    format='mixed'
)

# updating the format for average view duration
aggregated_metric_by_video['Average view duration'] = pd.to_timedelta(
    aggregated_metric_by_video['Average view duration']
)

aggregated_metric_by_video['Average view duration'] = (
    aggregated_metric_by_video['Average view duration'].apply(lambda x:
                                                      x.components.seconds
                                                      + x.components.minutes*60
                                                      + x.components.hours*3600))
