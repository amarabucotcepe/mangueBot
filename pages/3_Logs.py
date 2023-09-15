import streamlit as st
import sqlalchemy
import pandas as pd
import json

st.set_page_config(page_title='MangueBot | Logs', page_icon=':crab:', layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("Logs")

engine = sqlalchemy.create_engine('sqlite:///sqlite.db')

df = pd.read_sql_table('message_store', engine)
session = st.selectbox('Chat', df.session_id.unique())
messages = df.query(f"session_id == '{session}'")['message']
# df
for msg in messages:
    msg= json.loads(msg)
    if msg["type"] == "ai":
        st.chat_message(msg["type"]).write(msg["data"]["content"])
    elif msg["type"] == "human":    
       st.chat_message(msg["type"]).write(msg["data"]["content"])





