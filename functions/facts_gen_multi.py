import os
import pandas as pd
import streamlit as st
from anthropic import Anthropic
from underthesea import word_tokenize
from langchain.schema import Document
from langchain.vectorstores import Qdrant
from langchain.embeddings import CohereEmbeddings

#---CLAUDE-RESPONSE----------------------------------------------
def responding_claude(question, context):
    #---PROMPT-------------------------------------------------------
    prompt = f"You are a helpfull assistant that excel in answering questions from a given context.\
            You will be provided with the question which is delimited by XML tags and the \
            context delimited by triple backticks. \
            Base on this context, please answer the question for Vietnamese citizen in formal style.\
            If the context does not contain relevant information,\
            please answer that context is not enough information\
            <tag>{question}</tag>\
            ````\n{context}\n```"
    client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
    HUMAN_PROMPT = f"{prompt}\n\nHuman: "
    AI_PROMPT = "\n\nAssistant:"
    completion = client.completions.create(
        model="claude-2",
        max_tokens_to_sample=2000,
        temperature=0.1,
        prompt=f"{HUMAN_PROMPT} {AI_PROMPT}",
    )
    return completion.completion

def qdrant_faq_uploader(FACTS_DB, lang):
    class FAQdrant():
        def __init__(self, qdrant_url, qdrant_api_key, file_path):
            #Qdrant Key
            self.qdrant_url = qdrant_url
            self.qdrant_api_key = qdrant_api_key
            self.file_path = file_path        

            #Embedding using Cohere Multilingual
            self.embeddings = CohereEmbeddings(model="multilingual-22-12", 
                                            cohere_api_key=os.environ['COHERE_API_KEY'])

        def read_file(self):
            #Load data from file 
            df = pd.read_excel(self.file_path)
            #Remove all null answer
            self.df = df.dropna(subset=['Trả lời'])

        def langchain_docs(self):
            #Create Langchain Document including Question-Answer
            self.question_list = []
            self.vi_processed_question_list = []
            self.ids = []
            for i in range(len(self.df)):
                self.ids.append(i)
                single_question = Document(page_content=self.df.iloc[i,0], 
                                        metadata={'answer': self.df.iloc[i,1], 
                                                    'n_question': i})
                self.question_list.append(single_question)

                # Preprocessing with Underthesea
                self.df.iloc[i,0] = word_tokenize(self.df.iloc[i,0], format="text")
                vi_single_question = Document(page_content=self.df.iloc[i,0], 
                                        metadata={'answer': self.df.iloc[i,1], 
                                                    'n_question': i})
                self.vi_processed_question_list.append(vi_single_question)

        def upload_qdrant(self, docs, collection_name):
            #Upload Documents to Qdrant Online Storage
            Qdrant.from_documents(docs,
                                self.embeddings, 
                                url=self.qdrant_url, 
                                api_key=self.qdrant_api_key, 
                                content_payload_key="page_content",
                                metadata_payload_key="metadata",
                                collection_name=collection_name,
                                )

        def processing(self):
            self.read_file()
            self.langchain_docs()
            self.upload_qdrant(self.question_list, 'faq')
            if lang == 'vi':
                self.upload_qdrant(self.vi_processed_question_list, 'faqVieProcessed')
            print('Uploaded Documents to Qdrant in 2 Collection faq and faqVieProcessed')
    #Finished
    FAQdrant(st.session_state.qdrant_url, 
             st.session_state.qdrant_api_key, 
             file_path=f'{FACTS_DB}/multiple_questions_gen.xlsx',
             ).processing()
    pass

def qdrant_context_uploader(context, lang):
    class DocsQdrant():
        def __init__(self, qdrant_url, qdrant_api_key, file_path: str=None, context:str=None, lang:str=None):
            #Qdrant Key
            self.qdrant_url = qdrant_url
            self.qdrant_api_key = qdrant_api_key
            self.file_path = file_path  
            self.context = context      
            self.lang = lang
            #Embedding using Cohere Multilingual
            self.embeddings = CohereEmbeddings(model="multilingual-22-12", 
                                            cohere_api_key=os.environ['COHERE_API_KEY'])

        def read_file(self):
            # Load context from txt file
            with open(self.file_path, 'r') as f:
                _context = f.read()
            # Split to small chunks, delimited by '\n\n'
            self.context_list = _context.split('\n\n')

        def langchain_docs(self):
            #Create Langchain Document including Question-Answer
            self.context_list = []
            self.vi_processed_context_list = []
            self.ids = []
            for i in range(len(self.context_list)):
                self.ids.append(i)
                single_context = Document(page_content=self.context_list[i], 
                                        metadata={'n_context': i})
                self.context_list.append(single_context)

                # Preprocessing with Underthesea
                self.context_list[i] = word_tokenize(self.context_list[i], format="text")
                vi_single_context = Document(page_content=self.context_list[i], 
                                        metadata={'n_context': i})
                self.vi_processed_context_list.append(vi_single_context)

        def upload_qdrant(self, docs, collection_name):
            #Upload Documents to Qdrant Online Storage
            Qdrant.from_documents(docs,
                                self.embeddings, 
                                url=self.qdrant_url, 
                                api_key=self.qdrant_api_key, 
                                content_payload_key="page_content",
                                metadata_payload_key="metadata",
                                collection_name=collection_name,
                                )

        def processing(self):
            if self.context is not None:
                self.context_list = self.context.split('\n\n')
            else:
                self.read_file()
            self.langchain_docs()
            self.upload_qdrant(self.context_list, 'context')
            if self.lang == 'vi':
                self.upload_qdrant(self.vi_processed_question_list, 'contextVieProcessed')
            print('Uploaded Documents to Qdrant in 2 Collection context and contextVieProcessed')
    #Finished
    DocsQdrant(st.session_state.qdrant_url, 
             st.session_state.qdrant_api_key, 
             context=context,
             lang=lang).processing()

    pass
