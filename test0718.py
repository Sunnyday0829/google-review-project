import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

### ========== ###

# Page Configuration
st.set_page_config(
    page_title = "Audi Customer Reviews Dashboard",
    page_icon = "./my_icon.png",
    layout = "wide", # centered/wide
    initial_sidebar_state = "auto", # auto/expanded/collapsed
    menu_items={
        'About': "Established by Sunny Hsu 2023 Summer"
    }
)

# Page Title
st.title(':red_car: Audi Customer Reviews Dashboard')

### ========== ###

# Read Data
data_outscraper = pd.read_csv("./20230717055154221d.csv")
data = data_outscraper[['name','reviews','rating','review_text','owner_answer','owner_answer_timestamp_datetime_utc','review_rating','review_datetime_utc','review_likes']]

### ========== ###

# Page Sidebar
with st.sidebar:
    selectbox_value = st.multiselect(
        "Choose a Location",
        data['name'].unique()
    )

### ========== ###

# Filtered Data
data = data[data['name'].isin(selectbox_value)]

# 展示 DataFrame
st.dataframe(data.head(n = 5))

# 顯示資料型態
st.text(data.dtypes)

# 表格
data_ratings = data.groupby(by = "name")['rating'].mean().reset_index()
st.dataframe(data_ratings)

data_rating_percentage = data.sort_values('review_rating').groupby(['name','review_rating'])['review_rating'].count().reset_index(name = 'count')
st.dataframe(data_rating_percentage)

# 畫圖
fig_ratings = px.bar(data_ratings, 
             x = "rating", y = "name", 
             orientation = 'h',
             title = "Overall Ratings",
             text_auto = True,
             color = 'rating', color_continuous_scale=['#bcbcbc', '#de0909'])
fig_ratings.update_traces(textfont_size = 12, textangle = 0, textposition = 'outside', cliponaxis = False)
fig_ratings.update_layout(plot_bgcolor = 'white', 
                  xaxis_title = 'Ratings', yaxis_title = "Location",
                  font = dict(size = 12, color = 'black'),
                  coloraxis_showscale = False)


fig_rating_percentage = px.histogram(data_rating_percentage, x = "name",
                    y = "count", color = "review_rating",
                    barnorm = 'percent', text_auto = True,
                    title = "Past 3 Months Ratings Percentage",
                    category_orders={"review_rating" : [1,2,3,4,5]},
                    color_discrete_map={1:'#ffbaba', 2:'#ff7b7b', 3:'#ff5252', 4:'#ff0000', 5:'#a70000'})
fig_rating_percentage.update_traces(textfont_size = 12, textangle = 0, textposition = 'inside', cliponaxis = False)
fig_rating_percentage.update_layout(plot_bgcolor = 'white', 
                  xaxis_title = 'Location', yaxis_title = "Percentage",
                  font = dict(size = 12, color = 'black'))

### ========== ###

# Construct Tabs and Columns for Page Layout
tab1, tab2 = st.tabs(["Overview", "Highlighted Reviews"])

with tab1:

    st.plotly_chart(fig_ratings,
                    use_container_width = True)
    st.plotly_chart(fig_rating_percentage,
                    use_container_width = True)

with tab2:

    st.subheader("Highlighted Reviews")
    st.dataframe(data_ratings)
    st.dataframe(data_rating_percentage)
    
