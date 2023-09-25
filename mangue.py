### sqlite3
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
###

import streamlit as st

from langchain.chains import ConversationalRetrievalChain
from langchain.callbacks import StreamlitCallbackHandler
from langchain.memory.chat_message_histories import SQLChatMessageHistory
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory

import uuid
import os
import requests
import json

def get_credentials():
    if not(os.path.isfile('credentials.json')):
        r = requests.get(st.secrets['CREDENTIALS_PATH'], verify=False)
        data = r.json()
        with open('credentials.json', 'w') as f:
            f.write(json.dumps(data))
    return 'credentials.json'

def get_eastereggs(prompt):
    if prompt.find('inovação') != -1:
        st.balloons()
        return True
    if prompt.find('licitação') != -1:
        st.snow()
        return True
    if prompt.find('direito') != -1:
        st.snow()
        return True
    return False

st.set_page_config(page_title='MangueBot', page_icon=':crab:', layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("Hello Mangue! :crab:")

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = session_id = 'mangue-'+str(uuid.uuid4())


chat_message_history = SQLChatMessageHistory(
    session_id=st.session_state['session_id'],
    connection_string='sqlite:///sqlite.db'
)

####
from langchain.chat_models import ChatVertexAI 

import google.auth

KEYS = get_credentials()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEYS
credentials, project_id = google.auth.load_credentials_from_file(KEYS)

###

os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
    
with st.sidebar:
    st.subheader('Modelo: Google - chat-bison')
    temperatura = st.slider('Criatividade', min_value=0, max_value=10, value=7, step=1)
    if st.button("Limpar", type='primary'):
        del st.session_state['session_id']
        del st.session_state['messages']
        st.experimental_rerun()

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Olá, eu sou o MangueBot, o seu assistente virtual sobre Mangue Beat. \
                                     Você pode me fazer perguntas, cantar uma música ou conversar sobre a Mangue Town 😄."}]
    chat_message_history.add_ai_message(st.session_state["messages"][0]["content"])

for msg in st.session_state.messages:
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    if msg["role"] == "assistant":
        st.chat_message(msg["role"], avatar='🦀').write(msg["content"])
        memory.chat_memory.add_ai_message(msg["content"])
    elif msg["role"] == "user":    
       st.chat_message(msg["role"], avatar='🕵️‍♂️').write(msg["content"], avatar=':user:')
       memory.chat_memory.add_user_message(msg["content"])
    else:    
       memory.chat_memory.add_message('system', msg["content"])


if prompt := st.chat_input('Mensagem'):

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar='🕵️‍♂️').write(prompt)
    chat_message_history.add_user_message(prompt)
    
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)


    with st.spinner('Pensando...'):
        # stream_handler = StreamlitCallbackHandler(st.empty())
        # llm = ChatOpenAI(model_name='gpt-3.5-turbo', streaming=True, temperature=temperatura/10, callbacks=[stream_handler])
        llm = ChatVertexAI(credentials=credentials, project_id=project_id, max_output_tokens=512, temperature=temperatura/10)
        qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=vectorstore.as_retriever(k=1), memory=memory)
        response = qa(prompt)
        
        msg = response['answer']
        chat_message_history.add_ai_message(msg)
        source = vectorstore.similarity_search(prompt)
        st.chat_message("assistant", avatar='🦀').write(msg)
        get_eastereggs(prompt)
        st.session_state.messages.append({"role": "assistant", "content": msg})
        with st.expander("Ver contexto"):
            for page in source:
                st.write(page.page_content)
