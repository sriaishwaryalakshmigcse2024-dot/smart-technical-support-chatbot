import streamlit as st
from ollama import RequestError, ResponseError

from feedback import save_feedback
from rag_chatbot import MODEL_NAME, generate_answer
from retriever import build_retriever, search_documents
from analytics import show_feedback_dashboard

# --------------------------------------------------
# 1. Configure the Streamlit page
# --------------------------------------------------

st.set_page_config(
    page_title="Smart Technical Support Chatbot",
    page_icon="🛠️",
    layout="centered",
)

st.title("🛠️ Smart Technical Support Chatbot")
st.caption(
    "Ask technical questions and get answers "
    "grounded in your knowledge base."
)


# --------------------------------------------------
# 2. Load the RAG retriever once and reuse it
# --------------------------------------------------

@st.cache_resource(show_spinner="Loading the knowledge base...")
def load_retriever():
    return build_retriever()


# --------------------------------------------------
# 3. Initialize conversation history
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# 4. Sidebar
# --------------------------------------------------

with st.sidebar:
    st.header("Chat Settings")
    st.write(f"**AI model:** {MODEL_NAME}")
    st.write("**Retrieval:** RAG")
    st.write("**Sources:** Technical knowledge base")
    st.divider()

    if st.button("📊 Feedback Analytics"):
        st.session_state.show_analytics = not st.session_state.get(
            "show_analytics", False
        )
        st.rerun()

    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption(
        "Answers are based on retrieved documents. "
        "Contact IT support if the information is insufficient."
    )
 # --------------------------------------------------
# Show or hide the feedback analytics dashboard
# --------------------------------------------------

if st.session_state.get("show_analytics", False):
    show_feedback_dashboard()
    st.divider()



# --------------------------------------------------
# 5. Display previous messages and save feedback
# --------------------------------------------------

for message_index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show feedback buttons only for assistant answers.
        if message["role"] == "assistant":
            feedback_key = f"feedback_{message_index}"

            # Find the question associated with this answer.
            question_index = message_index - 1
            if (
                question_index >= 0
                and st.session_state.messages[question_index]["role"] == "user"
            ):
                question = st.session_state.messages[question_index]["content"]

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "👍 Helpful",
                        key=f"helpful_{message_index}",
                        disabled=st.session_state.get(feedback_key) is not None,
                    ):
                        save_feedback(question, message["content"], "helpful")
                        st.session_state[feedback_key] = "helpful"
                        st.rerun()

                with col2:
                    if st.button(
                        "👎 Not helpful",
                        key=f"not_helpful_{message_index}",
                        disabled=st.session_state.get(feedback_key) is not None,
                    ):
                        save_feedback(question, message["content"], "not_helpful")
                        st.session_state[feedback_key] = "not_helpful"
                        st.rerun()

                feedback = st.session_state.get(feedback_key)

                if feedback == "helpful":
                    st.caption("Thanks for your feedback!")
                elif feedback == "not_helpful":
                    st.caption("Thanks. We'll use this feedback to improve.")

# --------------------------------------------------
# 6. Accept a new question
# --------------------------------------------------

question = st.chat_input(
    "Ask a technical support question..."
)

if question:
    # Save the user's question first.
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    try:
        with st.spinner(
            "Searching documents and generating an answer..."
        ):
            # Step A: Load the retrieval components.
            model, index, chunks = load_retriever()

            # Step B: Retrieve relevant passages.
            results = search_documents(
                question,
                model,
                index,
                chunks,
                top_k=3,
            )

            # Step C: Generate a grounded answer.
            answer = generate_answer(question, results)

    except ResponseError as error:
        answer = (
            "Ollama returned a model error. "
            "Please check that the llama3.2 model is available "
            "and try again."
        )
        st.error(f"{answer}\n\nTechnical details: {error}")

    except RequestError as error:
        answer = (
            "I couldn't connect to Ollama. "
            "Please make sure Ollama is installed and running, "
            "then try again."
        )
        st.error(f"{answer}\n\nTechnical details: {error}")

    except Exception as error:
        answer = (
            "Something went wrong while processing your question. "
            "Please check the terminal for details and try again."
        )
        st.error(answer)
        print(f"Unexpected chatbot error: {error}")

    # Save the assistant's answer to conversation history.
    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

    # Rerun so Step 5 displays the answer and feedback buttons.
    st.rerun()

