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
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient


class DocProcessing():
    def __init__(self, 
                 uploaded_file,
                 vector_path:str='vectordb',
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
    def file_processing(self):
        self.file_input()
        self.file_loading()
        self.text_splitting()
        # self.display_chunks_hist()
        self.chroma_vectorization()
        st.write('Processed Document to VectorDatabase!')
        
        # if self.vectordb != "existed":
        #     self.file_loading()
        #     self.text_splitting()
        #     if self.chunks_plot==True:
        #         token_size = [self.tiktoken_len(self.chunks[i]) for i in range(len(self.chunks))]
        #         self.token_counts_plot(token_size)
        #     if self.vmethod == 'qdrant':
        #         self.vectorization()
        #     elif self.vmethod == 'chroma':
        #         self.chroma_vectorization()
        #     else:
        #         print("Please select vectordatabase method: 'qdrant' or 'chroma'")
        # else:
        #     if self.vmethod == 'qdrant':
        #         self.vectordb_loading()
        #     elif self.vmethod == 'chroma':
        #         self.chroma_loading()
        #     else:
        #         print("Please select vectordatabase method: 'qdrant' or 'chroma'")
        # return self.vdatabase
        
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
        import plotly.express as px
        # Create histogram using Plotly
        fig = px.histogram(token_counts, nbins=30)
        # Customize the plot info
        fig.update_layout(
            title="Chunks-Size Histogram",
            xaxis_title="Chunk-Size",
            yaxis_title="Number of chunks",
            bargap=0.1,
            showlegend=False)
        # Display the plot
        st.plotly_chart(fig, use_container_width=True)
        
    def display_chunks_hist(self):
        if self.file_extension in [".pdf"]:
            token_counts = [self.tiktoken_len(chunk.page_content) for chunk in self.chunks]
        else:
            token_counts = [self.tiktoken_len(chunk) for chunk in self.chunks]
        self.token_counts_plot(token_counts)
        
    def total_number_of_chunks(self):
        return len(self.chunks)
    
    def display_chunks(self, n_chunk):
        return self.chunks
        # st.subheader(f'Chunk {n_chunk}:')
        # if self.file_extension in [".pdf"]:
        #     st.write(self.chunks[n_chunk].page_content)
        # else:
        #     st.write(self.chunks[n_chunk])
                
    def vectorization(self):
        ##Process-PDF-------------------------------
        if self.file_extension in [".pdf"]:
            ###Online-Mode--------------------------
            self.vdatabase = Qdrant.from_documents(self.chunks,
                                            self.embeddings, 
                                            url=self.qdrant_url, 
                                            prefer_grpc=True, 
                                            api_key=self.qdrant_api_key, 
                                            path=self.vector_path,
                                            collection_name=self.collection_name,
                                            )
        ##Process-DOCX-------------------------------
        if self.file_extension in [".doc", ".docx"]:
            ###Online-Mode--------------------------
            self.vdatabase = Qdrant.from_texts(self.chunks,
                                            self.embeddings, 
                                            url=self.qdrant_url, 
                                            prefer_grpc=True, 
                                            api_key=self.qdrant_api_key, 
                                            path=self.vector_path,
                                            collection_name=self.collection_name,
                                            )
        print("Qdrant Vectorized Chunks use on-disk storage\n")
    
    def vectordb_loading(self):
        if "vdatabase" in globals() or "qdrant" in locals():
            del self.vdatabase
        if os.path.exists(self.vector_path):
            [os.remove(os.path.join(root, filename)) for root, dirs, files in os.walk(self.vector_path) \
                                                    for filename in files if filename.endswith(".lock")]

        client = QdrantClient(path=self.vector_path, prefer_grpc=True)
        self.vdatabase = Qdrant(client=client, collection_name=self.collection_name, embeddings=self.embeddings)
        print("Qdrant Database loaded from local storage\n")
        
    def chroma_vectorization(self):
        if self.file_extension in [".doc", ".docx"]:
            self.vdatabase = Chroma.from_texts(texts=self.chunks, embedding=self.embeddings, persist_directory=self.vector_path)
        elif self.file_extension in [".pdf"]:
            self.vdatabase = Chroma.from_documents(documents=self.chunks, embedding=self.embeddings, persist_directory=self.vector_path)
        else:
            print('this may an error')
        self.vdatabase.persist()
        # self.vdatabase = None
        print("Chroma Database located on local storage\n")
        
    def chroma_loading(self):
        self.vdatabase = Chroma(persist_directory=self.vector_path, embedding_function=self.embeddings)
        print("Chroma Database loaded from local storage\n")

