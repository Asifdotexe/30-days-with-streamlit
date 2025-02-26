"""
Day 4 out of 30
Building a YouTube dashboard using the following data
link: https://www.kaggle.com/datasets/kenjee/ken-jee-youtube-data

@author: Asif Sayyed
Module initiated: 23-02-2025
Last Modified: 26-02-2025
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
    # ensuring that the datatypes are readable and understandable on the dashboard
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
        aggregated_metric_by_video['Average view duration'].apply(
            lambda x:
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

# running the function to load the datasets
(df_aggregated_metric_by_video, df_aggregated_metric_by_subs,
 df_comment_data, df_time_series_data) = load_data()

# additional feature engineering before building the app

# Determine the median metrics of videos published in the last 12 months.
# This helps analyze recent performance trends while excluding older videos
# that might have accumulated more views over time,
# leading to skewed statistics.
# Get the latest video publish time
# and subtract 12 months to define the cutoff date.
metric_date_12_month = (df_aggregated_metric_by_video['Video publish time'].max()
                        - pd.DateOffset(months=12))

# Filter videos published within the last 12 months and calculate their median metrics.
# This ensures a fair comparison by focusing on recent content.
median_aggregation = df_aggregated_metric_by_video[
    df_aggregated_metric_by_video['Video publish time']
    >= metric_date_12_month].median()

# Create differences from the median for numeric values only.
# This normalizes data by measuring the percentage difference from the median.
# Useful for understanding how much each value deviates from the typical value.

# Identify numeric columns (float64 or int64).
numeric_cols = np.array((df_aggregated_metric_by_video.dtypes == 'float64')
                        | (df_aggregated_metric_by_video.dtypes == 'int64'))

# Subtract the median and divide by the median to get relative differences.
df_aggregated_metric_by_video.iloc[:, numeric_cols] = (
        df_aggregated_metric_by_video.iloc[:, numeric_cols]
        - median_aggregation).div(median_aggregation)

# Merge daily performance data with video publish dates
# to calculate the number of days since publication.

# Merge `df_time_series_data`
# (daily data) with `df_aggregated_metric_by_video`,
# keeping only the 'Video' and 'Video publish time' columns.
df_time_series_data = pd.merge(df_time_series_data,
                        df_aggregated_metric_by_video.loc[:,
                        ['Video', 'Video publish time']],
                        left_on='External Video ID', right_on='Video')

# Compute days since publication.
df_time_series_data['days_published'] = (
        df_time_series_data['Date']
        - df_time_series_data['Video publish time']
).dt.days

# Filter data to include only videos published in the last 12 months.

# Calculate the cutoff date,
# which is 12 months before the most recent video publish date.
date_12_months = (df_aggregated_metric_by_video['Video publish time'].max()
             - pd.DateOffset(months=12))

# Keep only rows where the video was published within the last 12 months.
df_time_diff_yr = df_time_series_data[df_time_series_data['Video publish time']
                                      >= date_12_months]

# Aggregate daily view data for the first 30 days:
# - Compute mean, median, 80th percentile, and 20th percentile of views per day.

views_days = pd.pivot_table(df_time_diff_yr, index='days_published', values='Views',
                            aggfunc=[np.mean, np.median,
                                     lambda x: np.percentile(x, 80),
                                     lambda x: np.percentile(x, 20)]
                            ).reset_index()

# Rename columns for clarity
views_days.columns = ['days_published', 'mean_views', 'median_views',
                      '80pct_views', '20pct_views']

# Keep only the first 30 days after publication
views_days = views_days[views_days['days_published'].between(0, 30)]

# Prepare cumulative view data for visualization
views_cumulative = views_days.loc[:, ['days_published', 'median_views',
                                      '80pct_views', '20pct_views']]

# Compute cumulative sum of median, 80th percentile, and 20th percentile views over time
views_cumulative.loc[:, ['median_views', '80pct_views', '20pct_views']] = \
    views_cumulative.loc[:, ['median_views', '80pct_views', '20pct_views']].cumsum()

# Starting the code for streamlit application from here

# creating a sidebar