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

st.set_page_config(
    page_title="Audi Customer Reviews Dashboard",
    page_icon="./my_icon.png",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'About': "Established by Sunny Hsu 2023 Summer"
    }
)

@st.cache_data
def load_and_preprocess_data(url):
    df = pd.read_excel(url)[['name','place_id','reviews','rating','review_text',
                             'owner_answer','owner_answer_timestamp_datetime_utc',
                             'review_rating','review_datetime_utc','review_likes']]
    
    df['city'] = df['place_id'].apply(get_place_details)
    df['brand'] = df['name'].apply(lambda name: identify_brand_func(name, brand_dict))
    df['review_datetime_utc'] = pd.to_datetime(df['review_datetime_utc'], errors='coerce').dt.date
    df['review_datetime_utc'].fillna(three_months_ago, inplace=True)
    df['date_difference'] = df['review_datetime_utc'].apply(lambda date: (current_date - date).days)
    df['within_three_months'] = df['date_difference'] <= 90
    return df

@st.cache_data
def get_place_details(place_id):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&language=en-TW&key=AIzaSyCLRZuF3hRmB4_-m4eeKZQ4ng-z4a6JguY"
    place_info = requests.get(url).json()
    address = place_info['result']['formatted_address'].split(",")
    try :
        city = next(ad.strip() for ad in address if 'City' in ad or 'County' in ad)
    except StopIteration:
        city = "Taoyuan City"
    return city

def identify_brand_func(name, brand_dict):
    for brand in brand_dict:
        if brand in name:
            return brand_dict[brand]
    return 'M-Benz'

def plot_bar_ratings(df, brand):
    df_brand = df[(df['brand'] == brand) & (df['city'].isin(selectbox_value_location))]
    df_brand = df_brand.groupby("name")['rating'].mean().reset_index().sort_values('rating')
    
    fig = px.bar(df_brand, x="rating", y="name", orientation='h', color='rating', color_continuous_scale=['#bcbcbc', '#de0909'], text_auto=True)
    fig.update_traces(textfont_size=12, textangle=0, textposition='outside', cliponaxis=False)
    fig.update_layout(plot_bgcolor='white', xaxis_title='Ratings', yaxis_title="", font=dict(size=12, color='black'), coloraxis_showscale=False)
    fig.update_xaxes(showgrid=False)
    return fig

def plot_hist_within3months_ratings_percentage(df):
    data_within_months_ratings = df[(df['within_three_months']) & (df['city'].isin(selectbox_value_location))].sort_values('review_rating')
    data_within_months_ratings = data_within_months_ratings.groupby(['brand','review_rating'])['review_rating'].count().reset_index(name = 'count').sort_values('brand', ascending=False)
    fig = px.histogram(data_within_months_ratings, 
                     x = "brand", y = "count", 
                     color = "review_rating",
                     barnorm = 'percent', text_auto = True,
                     category_orders={"review_rating" : [1,2,3,4,5]},
                     color_discrete_map={1:'#ffbaba', 2:'#ff7b7b', 3:'#ff5252', 4:'#ff0000', 5:'#a70000'})
    fig.update_traces(texttemplate='%{y:.2s}%', textposition='inside', 
                      textfont_size=12, textangle=0, cliponaxis=False)
    fig.update_layout(plot_bgcolor = 'white', 
                      xaxis_title = '', yaxis_title = '',
                      font = dict(size = 12, color = 'black'),
                      legend = dict(yanchor = 'bottom', xanchor = 'center', orientation = 'h', x = 0.5, y = -0.3))
    fig.update_xaxes(showgrid=False)
    return fig

def plot_pie_ratings(df, brand):
    data_within_months_ratings = df[(df['within_three_months']) & (df['brand'] == brand) & (df['city'].isin(selectbox_value_location))].sort_values('review_rating', ascending=False)
    data_within_months_ratings = data_within_months_ratings.groupby(['brand','review_rating'])['review_rating'].count().reset_index(name = 'count').sort_values(['brand', 'review_rating'], ascending=[False, False])
    fig = px.pie(data_within_months_ratings, values='count', names='review_rating', hole=.3,
                 color_discrete_map={1.0: '#e81000',
                                     2.0: '#f76055',
                                     3.0: '#ff9189',
                                     4.0: '#ffcaca',
                                     5.0: '#ffdbdb'})
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig



def data_lower_3(df):
    data_review_lower3 = df[(df['review_rating'] <= 3) & (df['brand'] == "Audi") & (df['city'].isin(selectbox_value_location))]
    data_review_lower3 = data_review_lower3[['name', 'review_text', 'owner_answer', 'review_rating', 'review_datetime_utc']].sort_values('review_datetime_utc', ascending = False)
    return data_review_lower3

current_date = datetime.now().date()
three_months_ago = current_date - timedelta(days=90)
brand_dict = {'Audi': 'Audi', 'BMW': 'BMW'}

data = load_and_preprocess_data("./complete_review.xlsx")
brands = ['Audi', 'BMW', 'M-Benz']

st.sidebar.header("Audi Customer Reviews Dashboard `version 1`")
st.sidebar.subheader('Select Location')


with st.sidebar:

  selectbox_value_location = st.sidebar.multiselect(
      "Loaction",
      data['city'].unique(),
      ["Taipei City", "New Taipei City"]
  )

st.sidebar.markdown('''
---
Created by Brian Wu, Johannes Hobel, Sunny Hsu.
''')
st.sidebar.markdown('''
Visit [Github Page](https://github.com/Sunnyday0829/google-review-project) for more detail :speech_balloon:.
''')

st.image('./banner.jpg', use_column_width=True)

tab1, tab2, tab3 = st.tabs(["Overview", "Highlighted Reviews", "Semantic Analysis"])

with tab1:

    st.markdown('### Overall Ratings Comaprison')
    col1, col2, col3 = st.columns(3)

    with col1 : 
        st.subheader("Audi")
        st.plotly_chart(plot_bar_ratings(data, brands[0]), use_container_width=True)

    with col2 :
        st.subheader("BMW")
        st.plotly_chart(plot_bar_ratings(data, brands[1]), use_container_width=True)

    with col3 :
        st.subheader("M-Benz")
        st.plotly_chart(plot_bar_ratings(data, brands[2]), use_container_width=True)

    st.markdown('### Within 3 Months Ratings Comparison')
    col4, col5, col6 = st.columns(3)

    with col4 :
        st.subheader("Audi")
        st.plotly_chart(plot_pie_ratings(data, brands[0]), use_container_width=True)

    with col5 :
        st.subheader("BMW")
        st.plotly_chart(plot_pie_ratings(data, brands[1]), use_container_width=True)

    with col6 :
        st.subheader("M-Benz")
        st.plotly_chart(plot_pie_ratings(data, brands[2]), use_container_width=True)

with tab2:

    st.markdown('### Highlighted Reviews (lower than 3)')
    st.dataframe(data_lower_3(data), use_container_width=True)

with tab3:
    st.markdown('### Semantic Analysis')