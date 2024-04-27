import streamlit as st
from dataclasses import dataclass
import sys
import os
sys.path.append('D:/CodePhilly')
import back
import base64
import pangea.exceptions as pe
from pangea.config import PangeaConfig
from pangea.services import Redact
@st.cache_data
def process_chat_input(chat_message,tool):
    # chat_message=mask_with_redact(chat_message)
    # response = back2.start(chat_message,tool)
    if tool=="General":
        response=back.O_LLM_gemini(chat_message)
    elif tool=="Email Manager":
        response=back.write_email(chat_message)
    elif tool=="Web Surfer":
        response=back.internet(chat_message)
    elif tool=="Report Analyst":
        response=back.generate_report(chat_message)
    elif tool=='Inventory Manager':
        response=back.Inventory_Management_Handler(chat_message)
    elif tool=='Catalogue Business Analyst':
        response=back.Report_catalogue(chat_message)
        print("response: ",response)
        print(type(response))
    return response

@dataclass
class Message:
    actor: str
    payload: str

def main(code):
    # a,b,c,d,e,g=back.google_sheets_access()
    usr=get_user(code)
    usr=st.session_state.usr_name
    st.sidebar.title('Up!'+'\n'+'Welcome '+usr)
    btn=st.sidebar.selectbox('Choose what you want to work with',['General','Web Surfer','Inventory Manager', 'Report Analyst', 'Email Manager','Catalogue Business Analyst'])
    print(btn)
    USER = "user"
    ASSISTANT = "ai"
    MESSAGES = "messages"

    if MESSAGES not in st.session_state:
        st.session_state[MESSAGES] = [Message(actor=ASSISTANT, payload="Hi! How can I help you?")]

    for msg in st.session_state[MESSAGES]:
        st.chat_message(msg.actor).write(msg.payload)
    prompt = st.chat_input("Ask a question!")
    
    if prompt:
        prompt=mask_with_redact(prompt)
        st.session_state[MESSAGES].append(Message(actor=USER, payload=prompt))
        st.chat_message(USER).write(prompt)
        response = process_chat_input(prompt,btn)
        if len(response)==3 and btn=='Inventory Manager':
            st.write('Old Data Frame')
            st.dataframe(response[0])
            st.write('Latest Data Frame')
            st.dataframe(response[1])
            st.session_state[MESSAGES].append(Message(actor=ASSISTANT, payload=response))
            st.chat_message(ASSISTANT).write(response[2])
        elif btn=='Report Analyst' and response=='Report Generated':
            st.session_state[MESSAGES].append(Message(actor=ASSISTANT, payload=response))
            st.chat_message(ASSISTANT).write(response)
            with open('Report_vendor_gemini.pdf', "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                pdf_display = F'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
                st.markdown(pdf_display, unsafe_allow_html=True)
            #btn=='Catalogue Business Analyst'
        elif btn=='Catalogue Business Analyst':
            st.session_state[MESSAGES].append(Message(actor=ASSISTANT, payload=response))
            st.chat_message(ASSISTANT).write(response)
        else:
            st.session_state[MESSAGES].append(Message(actor=ASSISTANT, payload=response))
            st.chat_message(ASSISTANT).write(response)
def get_user(c):
    import pangea.exceptions as pe
    from pangea.config import PangeaConfig
    from pangea.services.authn.authn import AuthN

    token = ''
    domain = ''

    # Configure Pangea SDK with provided domain
    config = PangeaConfig(domain=domain)
    # Initialize the AuthN service with the token and configuration
    if st.session_state.usr_name is None:
        authn = AuthN(token, config=config, logger_name="pangea")
        usr = authn.client.userinfo(c)
        print("He;;p\n"+str(usr))
        usr= usr.raw_result['refresh_token']['profile']['first_name'] 
        st.session_state.usr_name=usr
    return st.session_state.usr_name

def mask_with_redact(prompt):
    token = ""
    domain = ""
    config = PangeaConfig(domain=domain)
    redact = Redact(token, config=config)
    try:
        redact_response = redact.redact(text=prompt)
    except pe.PangeaAPIException as e:
        print(f"Embargo Request Error: {e.response.summary}")
        for err in e.errors:
            print(f"\t{err.detail} \n")
    return redact_response.result.redacted_text

if __name__ == "__main__":
        # if 'f' not in st.session_state:
        #     st.session_state.f=True
        if 'usr_name' not in st.session_state:
            st.session_state.c = st.query_params.get_all('code')
            st.session_state.usr_name=None
            print(st.session_state.c)
        main(st.session_state.c[0])