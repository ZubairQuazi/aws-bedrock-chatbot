import os
import streamlit as st
from langchain_aws import ChatBedrockConverse
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

st.set_page_config(page_title="AWS Bedrock GenAI Chatbot", page_icon="💬", layout="centered")

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

st.title("💬 AWS Bedrock Generative AI Chatbot")
st.caption("A simple Streamlit chatbot using LangChain and Anthropic Claude 3 Haiku on Amazon Bedrock.")

with st.sidebar:
    st.subheader("Configuration")
    st.write(f"**AWS Region:** `{AWS_REGION}`")
    st.write(f"**Model ID:** `{MODEL_ID}`")
    st.info("The app uses the EC2 instance role for AWS credentials. Do not add access keys to this code.")
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask a question…")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                llm = ChatBedrockConverse(
                    model=MODEL_ID,
                    region_name=AWS_REGION,
                    temperature=0.3,
                    max_tokens=700,
                )
                history = [
                    SystemMessage(content="You are a helpful assistant. Give clear, accurate answers. If you are unsure, say so."),
                ]
                for item in st.session_state.messages[:-1]:
                    if item["role"] == "user":
                        history.append(HumanMessage(content=item["content"]))
                    else:
                        history.append(AIMessage(content=item["content"]))
                history.append(HumanMessage(content=prompt))
                response = llm.invoke(history)
                answer = response.content
                if isinstance(answer, list):
                    answer = "\n".join(
                        part.get("text", str(part)) if isinstance(part, dict) else str(part)
                        for part in answer
                    )
                answer = str(answer)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as exc:
                st.error("The request to Amazon Bedrock failed. Check the troubleshooting notes in README.md.")
                st.code(str(exc))
