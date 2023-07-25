import pandas as pd
import numpy as np
import matplotlib as plt
import plotly.express as px
import plotly.graph_objects as go
import plost
import requests
import json
import streamlit as st
from datetime import datetime
from datetime import timedelta

### === Page Configuration === ###

st.set_page_config(
    page_title = "Audi Customer Reviews Dashboard",
    page_icon = "./my_icon.png",
    layout = "wide", # centered/wide
    initial_sidebar_state = "auto", # auto/expanded/collapsed
    menu_items={
        'About': "Established by Sunny Hsu 2023 Summer"
    }
)

### === Read Data === ###

@st.cache_data
def load_data(url):
    df = pd.pd.read_excel(url)[['name','place_id','reviews','rating','review_text',
                                'owner_answer','owner_answer_timestamp_datetime_utc',
                                'review_rating','review_datetime_utc','review_likes']]
    return df

data_outscraper = load_data("./complete_review.xlsx")
data = data_outscraper[['name','place_id','reviews','rating','review_text',
                        'owner_answer','owner_answer_timestamp_datetime_utc',
                        'review_rating','review_datetime_utc','review_likes']]

### === Data Preprocessing === ###

# 定義獲取城市信息的函數
@st.cache_resource
def get_place_details(place_id):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&language=en-TW&key=AIzaSyCLRZuF3hRmB4_-m4eeKZQ4ng-z4a6JguY"
    place_info = requests.get(url).json()
    address = place_info['result']['formatted_address'].split(",")
    try :
        city = next(ad.strip() for ad in address if 'City' in ad or 'County' in ad)
    except StopIteration:
        city = "Taoyuan City"
    return city

# 應用函數獲取城市信息
data['city'] = data['place_id'].apply(get_place_details)

# 定義品牌識別函數
def identify_brand_func(name, brand_dict):
    for brand in brand_dict:
        if brand in name:
            return brand_dict[brand]
    return 'M-Benz'

# 應用函數識別品牌
brand_dict = {'Audi': 'Audi', 'BMW': 'BMW'}
data['brand'] = data['name'].apply(lambda name: identify_brand_func(name, brand_dict))

# 获取当前日期
current_date = datetime.now().date()

# 创建三个月前的日期
three_months_ago = current_date - timedelta(days=90)

# 转换 'review_datetime_utc' 列为 datetime 类型，并删除时间部分
data['review_datetime_utc'] = pd.to_datetime(data['review_datetime_utc'], errors='coerce').dt.date

# 将日期缺失值设为三个月前的日期
data['review_datetime_utc'].fillna(three_months_ago, inplace=True)

# 计算 'review_datetime_utc' 列与当前日期的差值
data['date_difference'] = data['review_datetime_utc'].apply(lambda date: (current_date - date).days)

# 判断差值是否小于等于 90 天（大致相当于 3 个月）
data['within_three_months'] = data['date_difference'] <= 90

### === Page Sidebar === ###

st.sidebar.header("Audi Customer Reviews Dashboard `version 1`")
st.sidebar.subheader('Select Location')

with st.sidebar:
    selectbox_value_location = st.multiselect(
        "Loaction",
        data['city'].unique()
    )

st.sidebar.markdown('''
---
Created by Brian Wu, Johannes Hobel, Sunny Hsu.
''')
st.sidebar.markdown('''
Visit [Github Page](https://github.com/Sunnyday0829/google-review-project) for more detail :speech_balloon:.
''')

### === Plots === ###

# ratings bar plot
data_ratings_audi = data[(data['brand'] == 'Audi') & (data['city'].isin(selectbox_value_location))]
data_ratings_audi = data_ratings_audi.groupby("name")['rating'].mean().reset_index().sort_values('rating')

data_ratings_bmw = data[(data['brand'] == 'BMW') & (data['city'].isin(selectbox_value_location))]
data_ratings_bmw = data_ratings_bmw.groupby("name")['rating'].mean().reset_index().sort_values('rating')

data_ratings_benz = data[(data['brand'] == 'M-Benz') & (data['city'].isin(selectbox_value_location))]
data_ratings_benz = data_ratings_benz.groupby("name")['rating'].mean().reset_index().sort_values('rating')

fig_ratings_hist_audi = px.bar(data_ratings_audi, 
                               x = "rating", y = "name",
                               orientation = 'h',
                               color = 'rating', color_continuous_scale=['#bcbcbc', '#de0909'],
                               text_auto = True)
fig_ratings_hist_audi.update_traces(textfont_size = 12, textangle = 0, textposition = 'outside', cliponaxis = False)
fig_ratings_hist_audi.update_layout(plot_bgcolor = 'white', 
                                    xaxis_title = 'Ratings', yaxis_title = "",
                                    font = dict(size = 12, color = 'black'),
                                    coloraxis_showscale = False)
fig_ratings_hist_audi.update_xaxes(showgrid = False)

# within 3 month ratings percentage pie chart
data_within_months_ratings = data[(data['within_three_months']) & (data['city'].isin(selectbox_value_location))].sort_values('review_rating')
data_within_months_ratings = data_within_months_ratings.groupby(['brand','review_rating'])['review_rating'].count().reset_index(name = 'count').sort_values('brand', ascending = False)

fig_within_months_ratings_hist = px.histogram(data_within_months_ratings, 
                                              x = "brand", y = "count", 
                                              color = "review_rating",
                                              barnorm = 'percent', text_auto = True,
                                              category_orders={"review_rating" : [1,2,3,4,5]},
                                              color_discrete_map={1:'#ffbaba', 2:'#ff7b7b', 3:'#ff5252', 4:'#ff0000', 5:'#a70000'})
fig_within_months_ratings_hist.update_traces(texttemplate='%{y:.2s}%', textposition='inside', 
                                             textfont_size=12, textangle=0, cliponaxis=False)
fig_within_months_ratings_hist.update_layout(plot_bgcolor = 'white', 
                                             title_x = 0.5,
                                             xaxis_title = 'Location', yaxis_title = "Percentage",
                                             font = dict(size = 12, color = 'black'),
                                             legend = dict(yanchor = 'bottom', xanchor = 'center', orientation = 'h', x = 0.5, y = -0.3))

### === Construct Tabs and Columns for Page Layout === ###

# 
tab1, tab2, tab3 = st.tabs(["Overview", "Highlighted Reviews", "Semantic Analysis"])

with tab1:

    st.markdown('### Ratings Comaprison')

    st.plotly_chart(fig_ratings_hist_audi,
                    use_container_width = True)
    
    st.markdown('### Within 3 Months Ratings Percentage')

    st.plotly_chart(fig_within_months_ratings_hist,
                    use_container_width = True)


with tab2:

    st.subheader("Highlighted Reviews")
    st.dataframe(data.head(n = 10))

with tab3:

    st.markdown('### Semantic Analysis')






    