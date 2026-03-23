import streamlit as st
import pandas as pd
import plotly.express as px

# Title
st.title("Public Images of Science in Bulgaria (2011–2024)")

# Load data
df = pd.read_excel("data.xlsx")

# Show data
st.subheader("Dataset preview")
st.dataframe(df.head())

# Topic distribution
st.subheader("Topic distribution")
topic_counts = df['Topic'].value_counts().reset_index()
topic_counts.columns = ['Topic', 'Count']

fig = px.bar(topic_counts, x='Topic', y='Count')
st.plotly_chart(fig)

# Tone distribution
st.subheader("Tone distribution")
tone_counts = df['Tone'].value_counts().reset_index()
tone_counts.columns = ['Tone', 'Count']

fig2 = px.pie(tone_counts, names='Tone', values='Count')
st.plotly_chart(fig2)

# Timeline
st.subheader("Trends over time")
df['DatePosted'] = pd.to_datetime(df['DatePosted'])
df['year'] = df['DatePosted'].dt.year

timeline = df.groupby('year').size().reset_index(name='count')

fig3 = px.line(timeline, x='year', y='count')
st.plotly_chart(fig3)