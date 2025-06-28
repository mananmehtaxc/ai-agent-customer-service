import os
from io import StringIO
import streamlit as st
from langchain_community.document_loaders import TextLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ORIGINAL_FAQ_PATH = os.path.join(BASE_DIR, "faq.md")
UPLOADED_FAQ_PATH = os.path.join(BASE_DIR, "uploaded_faq.md")


def faq_manager_container():
    with st.sidebar:
        # st.container(height=500):
        st.markdown(
            """
            ### 📚 FAQ Manager

            This application uses a **pre-made FAQ file** (`faq.md`) by default.
            If you'd like, you can **upload your own FAQ (.md) file** below to override the default.
            """
        )

        if os.path.exists(ORIGINAL_FAQ_PATH):
            st.markdown("#### Original FAQ File")
            with open(ORIGINAL_FAQ_PATH, "r", encoding="utf-8") as f:
                original_faq_content = f.read()
            st.code(original_faq_content[:230] + ("..." if len(original_faq_content) > 1000 else ""), language="markdown")
            with open(ORIGINAL_FAQ_PATH, "r", encoding="utf-8") as f:
                data = f.read()
            st.download_button(
                label="⬇️ Download original FAQ file Preview",
                data=data,
                file_name="original_faq.md",
                mime="text/markdown",
            )
        else:
            st.warning("Original FAQ file not found. Please upload a new one.")

        uploaded_file = st.file_uploader("Upload your own FAQ (.md) file", type=["md"])

        
        if uploaded_file is not None: 
            file_text = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
            with open(UPLOADED_FAQ_PATH, "w", encoding="utf-8") as f:
                f.write(file_text)
            st.success("✅ Uploaded FAQ file is now active.")
            faq_path = UPLOADED_FAQ_PATH
        else:
            st.info("Using the original FAQ file.")
            faq_path = ORIGINAL_FAQ_PATH

        try:
            docs = TextLoader(faq_path).load()
            faq_content = docs[0].page_content
        except Exception as e:
            st.error(f"Failed to load FAQ file: {e}")
            faq_content = ""

        return faq_path, faq_content
