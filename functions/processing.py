import os
import tiktoken
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import CohereEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from underthesea import word_tokenize
from qdrant_client import QdrantClient
from langchain.vectorstores import Qdrant

class BookProcessing:
    def __init__(self, 
                 file_path:str=None,
                 vector_path:str=None,
                 chunk_size:int=500,
                 chunk_overlap:int=100,
                 collection_name:str=None,
                 chunks_plot:bool=False,
                 vectordb:str='non-existed',
                 vmethod:str='chroma',
                 book_lang:str='en',
                 ):
        self.file_path = file_path
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
        
    def file_process(self):
        if self.vectordb != "existed":
            self.file_loading()
            self.text_splitting()
            if self.chunks_plot==True:
                token_size = [self.tiktoken_len(self.chunks[i]) for i in range(len(self.chunks))]
                self.token_counts_plot(token_size)
            if self.vmethod == 'qdrant':
                self.vectorization()
            elif self.vmethod == 'chroma':
                self.chroma_vectorization()
            else:
                print("Please select vectordatabase method: 'qdrant' or 'chroma'")
        else:
            if self.vmethod == 'qdrant':
                self.vectordb_loading()
            elif self.vmethod == 'chroma':
                self.chroma_loading()
            else:
                print("Please select vectordatabase method: 'qdrant' or 'chroma'")
            
        return self.vdatabase
    
    def file_loading(self):
        _a, self.file_extension = os.path.splitext(self.file_path)
        if self.file_extension == ".pdf":
            loader = PyPDFLoader(self.file_path)
            self.data = loader.load_and_split()
            print('Loaded PDF file!\n')
    
        if self.file_extension in [".doc", ".docx"]:
            loader = Docx2txtLoader(self.file_path)
            self.data = loader.load()[0].page_content
            print('Loaded MS Word file!\n')
    
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
                    print(chunk_contents[0][:10])
                for j in range(len(chunk_contents)):
                    chunk = Document(page_content=chunk_contents[j], 
                                    metadata={'source': self.data[i].metadata['source'], 
                                            'page': self.data[i].metadata['page']})
                    self.chunks.append(chunk)
                pass
            print(len(self.data))
            print(len(self.chunks))
    
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


