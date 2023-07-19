import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.title('Uber pickups in NYC')

# 載入資料
data_outscraper = pd.read_csv("./20230717055154221d.csv")
data = data_outscraper[['name','reviews','rating','review_text','owner_answer','owner_answer_timestamp_datetime_utc','review_rating','review_datetime_utc','review_likes']]

# 展示 DataFrame
st.dataframe(data.head(n = 5))

# 顯示資料型態
st.text(data.dtypes)

#
data_ratings = data.groupby(by = "name")['rating'].mean().reset_index()
st.dataframe(data_ratings)

# 畫圖
fig = px.bar(data_ratings, x = "rating", y = "name", orientation = 'h')

# 展示圖形
st.plotly_chart(fig)




    
