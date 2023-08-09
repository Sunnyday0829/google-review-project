# app.py
import streamlit as st
from textblob import TextBlob

def analyze_sentiment(text):
    blob = TextBlob(text)
    if blob.sentiment.polarity > 0:
        return 'Positive'
    elif blob.sentiment.polarity == 0:
        return 'Neutral'
    else:
        return 'Negative'

st.title('Streamlit & TextBlob Sentiment Analysis')

input_text = st.text_area('Enter text for sentiment analysis:')
if st.button('Analyze'):
    sentiment = analyze_sentiment(input_text)
    st.write(f'The sentiment of the text is: {sentiment}')
