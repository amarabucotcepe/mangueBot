import streamlit as st
import pandas as pd

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
# from langchain_experimental.sql import  SQLDatabaseChain
from langchain.callbacks import StreamlitCallbackHandler, get_openai_callback, FileCallbackHandler
from langchain.memory.chat_message_histories import SQLChatMessageHistory

from langchain.schema.messages import AIMessage, HumanMessage, SystemMessage
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.memory import ConversationTokenBufferMemory, ConversationBufferMemory
import uuid
import requests
import os
from mangue import get_credentials, get_eastereggs

st.set_page_config(page_title='MangueBot | Dados', page_icon=':crab:', layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("Análise de dados 🎲")
origem = 'https://portaldatransparencia.gov.br/download-de-dados/orcamento-despesa'
st.write('Dados:', origem)
with st.expander("Dicionário de dados"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    r = requests.get('https://portaldatransparencia.gov.br/pagina-interna/603417-dicionario-de-dados-orcamento-da-despesa', headers=headers, verify=False)
    table = pd.read_html(r.content, header=0)[0].dropna(axis=0)
    table
# dicionario = 'https://portaldatransparencia.gov.br/pagina-interna/603417-dicionario-de-dados-orcamento-da-despesa'
# st.write('Dicionario:', dicionario)

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = session_id = 'data-'+str(uuid.uuid4())
    
db = SQLDatabase.from_uri("sqlite:///orcamento.db")

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
    temperatura = st.slider('Criatividade', min_value=0, max_value=10, value=0, step=1, disabled=True)
    max_tokens = st.slider('Tamanho da resposta', min_value=128, max_value=2048, value=512, step=1)
    if st.button("Limpar", type='primary'):
        del st.session_state['session_id']
        del st.session_state['messages']
        st.experimental_rerun()

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Olá, eu sou o DataBot, o seu assistente virtual para dados. \
                                     Crio e executo consultas SQL, a partir de perguntas sobre dados do orçamento federal do exercício 2022."}]
    chat_message_history.add_ai_message(st.session_state["messages"][0]["content"])

for msg in st.session_state.messages:
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    if msg["role"] == "assistant":
        st.chat_message(msg["role"], avatar='🤖').write(msg["content"])
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

    with st.spinner('Pensando...'):
        long_llm = ChatVertexAI(credentials=credentials, project_id=project_id, max_output_tokens=max_tokens, temperature=temperatura/10)
        formater = PromptTemplate.from_template('Organize os seguintes dados no formato de uma tabela com valores em formato moeda: {input}') | long_llm
        # llm = ChatOpenAI(model_name='gpt-3.5-turbo-0613', streaming=True, temperature=temperatura/10, callbacks=[stream_handler])
        db_chain = create_sql_query_chain(long_llm, db)
        # db_chain = SQLDatabaseChain.from_llm(long_llm, db, verbose=True)
        with get_openai_callback() as cb:
            sql = db_chain.invoke({'question': prompt})
            # st.session_state.messages.append({"role": "assistant", "content": response})
            # st.chat_message("assistant", avatar='🤖').write(sql)
            result = db.run(sql)
            # st.chat_message("assistant", avatar='🤖').write(result)
            get_eastereggs(prompt)
            response = formater.invoke({'input': result})
            # msg = response.content
            # st.chat_message("assistant", avatar='🤖').write(response)
            st.chat_message("assistant", avatar='🤖').write(response.content)
            # st.chat_message("assistant", avatar='🤖').write(cb)
            # chat_message_history.add_ai_message(response.content)
    with st.expander("Ver SQL"):
            st.code(sql)
    st.session_state.messages.append({"role": "assistant", "content": response.content})
    # st.session_state.messages.append({"role": "assistant", "content": cb})
