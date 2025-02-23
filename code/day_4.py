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

# loading the dataset
aggregated_metric_by_video = pd.read_csv(
    "data/ken-jee-yt-data/Aggregated_Metrics_By_Video.csv")
# skipping the first row and including everything else
aggregated_metric_by_video = aggregated_metric_by_video.iloc[1:,:]

