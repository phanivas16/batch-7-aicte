import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import PyPDF2
#load environment variabels
load_dotenv()
#get api key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("API key not found .check your .env file .")
    st.stop()
#initialize groq client openai compatible
client =OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)
#page configuration
st.set_page_config(page_title="AI Study Buddy",
page_icon="🎓")
st.title("🎓AI STUDY BUDDY")
#side bar animation
st.markdown("""
<style>

/* Sidebar animation */
section[data-testid="stSidebar"] {
    animation: slideIn 0.5s ease-in-out;
}

/* Sidebar buttons hover effect */
section[data-testid="stSidebar"] button {
    transition: all 0.3s ease;
}

section[data-testid="stSidebar"] button:hover {
    transform: translateX(5px);
    background-color: #E1BEE7 !important;
}

/* Slide animation */
@keyframes slideIn {
    from {
        transform: translateX(-20px);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

</style>
""", unsafe_allow_html=True)

#multi caht system
if "chats" not in st.session_state:
    st.session_state.chats={}

if "current_chat" not in st.session_state:
    st.session_state.current_chat= None

#sidebar
with st.sidebar:
    st.title("your chats")

    if st.button("➕ New Chat"):
        chat_id=f"Chat{len(st.session_state.chats)+1}"
        st.session_state.chats[chat_id]=[]
        st.session_state.current_chat=chat_id
        st.rerun()
        
    st.divider()
    

    for chat_name in list(st.session_state.chats.keys()):
        if st.button(chat_name,key=chat_name):
            st.session_state.current_chat=chat_name
            st.rerun()

#if no chat exists,create one
if not st.session_state.chats:
    chat_id="Chat_1"
    st.session_state.chats[chat_id]=[]
    st.session_state.current_chat=chat_id
messages=st.session_state.chats[st.session_state.current_chat]
#display previous chat
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


#bottom controls
st.markdown("---")
#small toggle button
if "show_upload" not in st.session_state:
    st.session_state.show_upload=False
if st.button("➕ upload file"):
   if st.session_state.show_upload:
       st.session_state.show_upload= False
   else:
    st.session_state.show_upload=True
show_upload=st.session_state.show_upload
if show_upload:
    uploaded_file=st.file_uploader(
        "upload PDF or TXT",
        type=["pdf","txt"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        file_text=""

        if uploaded_file.type=="application/pdf":
            pdf_reader=PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text =page.extract_text()
                if text:
                    file_text+=text

            
        elif uploaded_file.type =="text/plain":
            file_text=uploaded_file.read().decode("utf-8")
        if file_text.strip()=="":
            st.error("no text found in file.")
        else:
            response=client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role":"system",
                        "content":"summarize the following notes in bullet points."},
                    {
                        "role":"user",
                        "content":file_text[:6000]
                    }
                ],
            temperature=0.5
                )
            summary =response.choices[0].message.content
        with st.chat_message("assistant"):
            st.markdown(summary)
        messages.append(
            {"role":"assistant","content":summary}
            )

#chat input
prompt = st.chat_input("ask your question...")
if prompt:
    #save user message
    messages.append(
        {"role":"user","content":prompt})
    #show user message
    with st.chat_message("user"):
        st.markdown(prompt)
    if len(messages)==1:
        new_title=prompt[:30]+"...." if len(prompt)>30 else prompt
        st.session_state.chats[new_title]=st.session_state.chats.pop(
            st.session_state.current_chat
        )
        
        st.session_state.current_chat=new_title
        

  
    
    #prepare conversation
    api_messages=[
                {"role":"system",
                 "content":
                     "you are a helpful ai study buddy."
                     "summarize in bullet points when asked."
                     "explain simply when asked."
                     "generate 5 mcqs with answer if user asks for quiz."
                     "at the end of every response ,ask a helpful follow-up question."
                 }
                ]
    #add previous conversation
    for msg in messages:
        api_messages.append({
                "role":msg["role"],
                "content":msg["content"]
                })
            
    #get ai response
    with st.chat_message("assistant"):
        with st.spinner("thinking"):
            response=client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=api_messages,
                temperature=0.7
            )

            
            reply = response.choices[0].message.content
    st.markdown(reply)
       
    #save assistant response
    messages.append({"role":"assistant","content":reply})
     
    
        
       
    



