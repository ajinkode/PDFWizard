import streamlit as st 
# from dotenv import load_dotenv
import pickle
from streamlit_extras.add_vertical_space import add_vertical_space
from PyPDF2 import PdfReader

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import time

import os


st.set_page_config(page_title='PDF Wizard', page_icon = "./chat.ico")


# Center the image
container = st.container()
col_centered = container.columns(3)
col_centered[1].image('./chat.jpg', width=200)

st.set_option('deprecation.showfileUploaderEncoding', False)
# Coding the sidebar
with st.sidebar:
    st.title("PDF Wizard 💬🤖")
    
    
    st.subheader("Effortlessly upload your PDFs and ask any questions related to the PDF.")
    st.markdown('''
        ## Steps:
        - Upload your desired PDF.
        - Ask questions related to the PDF!
                ''')
    
    

# Hide 'Made with Streamlit'
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
    

    
def main():
    st.header("Chat with PDF 💬")
    # load_dotenv()
    
    tempkey = st.text_input('Please provide your OpenAI API Key', placeholder='sk-xxxx')
    st.markdown("Get your OpenAI API Key [here](https://platform.openai.com/account/api-keys) ")

    pdf = st.file_uploader("Upload your PDF", type='pdf')
    
    # upload a pdf file
    
    
    if tempkey is not None:
        
        apikey = tempkey
    
        os.environ['OPENAI_API_KEY']=apikey
        
        if apikey:
            st.success("Successfully uploaded the key! Now please go ahead and upload your PDF.", icon="✅")
    
    
        if pdf is not None:
            pdf_reader = PdfReader(pdf)
        
            text = ""
            for page in pdf_reader.pages:
                text+=page.extract_text()
                
            # st.write(text)
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size = 1000,
                chunk_overlap=200,
                length_function=len
            )
            
            chunks = text_splitter.split_text(text=text)
            
            # st.write(chunks)
            
            # Create Embeddings
            store_name = pdf.name[:-4]
            
            if os.path.exists(f"{store_name}.pkl"):
                with open(f"{store_name}.pkl", "rb") as f:
                    VectorStore = pickle.load(f)
                    # st.write("Embeddings loaded from the Disk! Money saved!")
                    
            else:
                embeddings = OpenAIEmbeddings()
                VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
                with open(f"{store_name}.pkl", "wb") as f:
                    pickle.dump(VectorStore, f)
                    
                    
            # Accept user questions/query
            query = st.text_input("Ask questions about your PDF file: ")
            
            # processing the query
            if query:
                with st.spinner("Please wait, generating response..."):
                    docs = VectorStore.similarity_search(query=query, k=3)
                    llm = OpenAI(temperature=0,)
                    chain = load_qa_chain(llm=llm, chain_type="stuff")
                    
                    if st.button('Click to see the tokens consumed!'):
                        with get_openai_callback() as cb:
                            response = chain.run(input_documents=docs, question=query)
                            st.write("Total tokens and total cost associated: ")
                            st.write(cb)

                    response = chain.run(input_documents=docs, question=query)
                    st.subheader("Result:")
                    st.info(response, icon='ℹ️')
                    st.balloons()
                
    st.write("Made with ❤️ by [Ajinkya Kale](https://www.linkedin.com/in/ajinkode/)")
    
    
if __name__ == '__main__':
    main()
    
