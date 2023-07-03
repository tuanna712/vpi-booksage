import base64, os
import pdfplumber
import streamlit as st
import tiktoken
from docx import Document as docxDoc
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import CohereEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from underthesea import word_tokenize

class DocProcessing():
    def __init__(self, 
                 uploaded_file,
                 vector_path:str=None,
                 chunk_size:int=500,
                 chunk_overlap:int=100,
                 collection_name:str=None,
                 chunks_plot:bool=False,
                 vectordb:str='non-existed',
                 vmethod:str='chroma',
                 book_lang:str='en',
                 ):
        
        ##Self Definition--------------------------
        self.uploaded_file = uploaded_file
        self.vector_path = vector_path
        self.qdrant_url = "https://cd6b8c5a-501f-4449-b488-ea45d252239c.us-east-1-0.aws.cloud.qdrant.io:6333"
        self.qdrant_api_key = "arMcul7YcGwzI9AzmsvA8td7OjV1B2e2DjYl-5cfs0XgCpSx8mwY3w"
        self.embeddings = CohereEmbeddings(model="multilingual-22-12", cohere_api_key="4ECOTqDXJpIYhxMQhUZxY12PPSqvgtYFclJm4Gnz")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.collection_name = collection_name
        self.chunks_plot = chunks_plot
        self.vectordb = vectordb
        self.vmethod = vmethod
        self.book_lang = book_lang
        
        ##Processing...----------------------------
        self.file_input()
        self.file_loading()
        
    def file_input(self):
        if self.uploaded_file is not None:
                #Split file extension for detection of loading type
                self.file_extension = os.path.splitext(self.uploaded_file.name)[-1]
                #Load PDF file
                if self.file_extension == ".pdf":
                    self.document = pdfplumber.open(self.uploaded_file)
                    print('Loaded PDF file!\n')
                #Load MS Word file
                if self.file_extension in [".doc", ".docx"]:
                    self.document = docxDoc(self.uploaded_file)
                    print('Loaded MS Word file!\n')
                return self.document
            
    def file_loading(self):
        ##Process-PDF-------------------------------
        if self.file_extension == ".pdf":
            #Convert Pages to Document which interact with Langchain
            self.data = []
            for i in range(len(self.document.pages)):
                page = Document(page_content=self.document.pages[i].extract_text(), 
                                    metadata={'source': self.uploaded_file.name, 
                                            'page': i})
                self.data.append(page)
        ##Process-MS WORD---------------------------
        if self.file_extension in [".doc", ".docx"]:
            self.data = ""
            for p in self.document.paragraphs:
                self.data = self.data + "\n" + p.text
        
    def text_splitting(self):
        #Split to Smaller Texts
        text_splitter = RecursiveCharacterTextSplitter(
                                chunk_size=self.chunk_size,
                                chunk_overlap=self.chunk_overlap, #Overlaping = 40% of Chunksize
                                length_function=self.tiktoken_len,
                                # separators=['\n'],
                                separators=['\n\n\n\n','\n\n\n','\n\n', '\n', ' ', ''],
                                )
        ##Process-MS WORD---------------------------
        if self.file_extension in [".doc", ".docx"]:
            self.chunks = text_splitter.split_text(self.data)
            if self.book_lang=='vi':
                self.chunks = [word_tokenize(self.chunks[i], format="text") for i in range(len(self.chunks))]
            print(len(self.data))
            print(len(self.chunks))
        ##Process-PDF-------------------------------
        if self.file_extension in [".pdf"]:
            self.chunks = []
            for i in range(len(self.data)):
                chunk_contents = text_splitter.split_text(self.data[i].page_content)
                if self.book_lang=='vi':
                    chunk_contents = [word_tokenize(chunk_contents[i], format="text") for i in range(len(chunk_contents))]
                for j in range(len(chunk_contents)):
                    chunk = Document(page_content=chunk_contents[j], 
                                    metadata={'source': self.data[i].metadata['source'], 
                                            'page': self.data[i].metadata['page']})
                    self.chunks.append(chunk)
                pass
            print(len(self.data))
            print(len(self.chunks))
            
    def tiktoken_len(self, text):
        tokenizer = tiktoken.get_encoding('cl100k_base')
        tokens = tokenizer.encode(
            text,
            disallowed_special=()
        )
        return len(tokens)
    
    def token_counts_plot(self, token_counts):
        import seaborn as sns
        import matplotlib.pyplot as plt
        # Set style and color palette for the plot
        sns.set_style("whitegrid"); sns.set_palette("muted")
        # Create histogram
        plt.figure(figsize=(10, 5))
        sns.histplot(token_counts, kde=False, bins=15)
        # Customize the plot info
        plt.title("Token Counts Histogram"); plt.xlabel("Token Count"); plt.ylabel("Frequency")
        plt.show()
        