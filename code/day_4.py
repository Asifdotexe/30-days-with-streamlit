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


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame,
                        pd.DataFrame, pd.DataFrame]:
    """This function is responsible for loading the data and performing
    some wrangling and feature engineering, this is also wrapped with
    the streamlit cache decorator to ensure that we do not recall this
    more than once per session

    :return: tuple of 4 dataframes containing the aggregate metric by video,
    aggregate metric by subscriber and country,
    comments data and time series data respectively
    :rtype: tuple
    """
    # loading the aggregated metric by video dataset
    aggregated_metric_by_video = pd.read_csv(
        "data/ken-jee-yt-data/Aggregated_Metrics_By_Video.csv"
    )
    # skipping the first row and including everything else
    aggregated_metric_by_video = aggregated_metric_by_video.iloc[1:, :]

    # loading aggregated metric by country and subscriber status dataset
    aggregated_metric_by_subs = pd.read_csv(
        "data/ken-jee-yt-data/Aggregated_Metrics_By_Country_And_Subscriber_Status.csv"
    )

    # loading the comment and time series dataset
    comment_data = pd.read_csv("data/ken-jee-yt-data/All_Comments_Final.csv")
    time_series_data = pd.read_csv(
        "data/ken-jee-yt-data/Video_Performance_Over_Time.csv")

    # performing cleaning and feature engineering on aggregated metric by video dataset
    # updating the colum names
    # ensuring that the datatypes are readable and understable on the dashboard
    aggregated_metric_by_video.columns = ['Video', 'Video title',
                                          'Video publish time',
                                          'Comments added',
                                          'Shares', 'Dislikes', 'Likes',
                                          'Subscribers lost',
                                          'Subscribers gained',
                                          'RPM (USD)', 'CPM (USD)',
                                          'Average % viewed',
                                          'Average view duration', 'Views',
                                          'Watch time (hours)', 'Subscribers',
                                          'Your estimated revenue (USD)',
                                          'Impressions', 'Impressions CTR(%)']

    # updating the datatypes
    # ensuring that the data is in a format suitable for time series analysis
    aggregated_metric_by_video['Video publish time'] = pd.to_datetime(
        aggregated_metric_by_video['Video publish time'],
        # since the dateformat is %b %m, %y using mixed format to infer it
        format='mixed'
    )

    # updating the format for average view duration
    # in the code below, we are converting the average view duration column
    # into a timedelta object as currently it was just str object
    aggregated_metric_by_video['Average view duration'] = pd.to_timedelta(
        aggregated_metric_by_video['Average view duration']
    )

    # here, we convert every component into seconds unit and aggregate them
    # as we want to show the average view duration in units of seconds.
    aggregated_metric_by_video['Average view duration'] = (
        aggregated_metric_by_video['Average view duration'].apply(lambda x:
                                                                  x.components.seconds
                                                                  + x.components.minutes * 60
                                                                  + x.components.hours * 3600))

    # Creating a new feature called engagement ratio
    # By dividing the total interactions by the number of views,
    # you get a ratio that shows the level of user engagement relative
    # to how many people have seen the content.
    # A higher ratio indicates
    # that a larger proportion of viewers are interacting with the content.
    aggregated_metric_by_video['Engagement ratio'] = (
            aggregated_metric_by_video['Comments added']
            + aggregated_metric_by_video['Shares']
            + aggregated_metric_by_video['Dislikes']
            + aggregated_metric_by_video['Likes']
            / aggregated_metric_by_video['Views'])

    # creating a new metric to determine
    # how many views it takes on average to add one subscriber.
    aggregated_metric_by_video['Views to subscriber ratio'] = (
            aggregated_metric_by_video['Views']
            / aggregated_metric_by_video['Subscribers gained'])

    # sorting datapoints based on Video publish time
    # this is needed
    # to ensure we have the newer videos on the top of the dataframe
    aggregated_metric_by_video = aggregated_metric_by_video.sort_values(
        'Video publish time', ascending=False
    )

    time_series_data['Date'] = pd.to_datetime(time_series_data['Date'])

    return (aggregated_metric_by_video, aggregated_metric_by_subs,
            comment_data, time_series_data)
