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
            self.question_list = self.df['Câu hỏi'].tolist()
            self.ans_list = self.df['Trả lời'].tolist()

        def langchain_docs(self):
            #Create Langchain Document including Question-Answer
            self.question_list_2 = self.question_list
            self.fn_question_list = []
            self.vi_processed_question_list = []
            self.ids = []
            for i in range(len(self.question_list)):
                self.ids.append(i)
                single_question = Document(page_content=self.question_list[i],
                                        metadata={'answer': self.ans_list[i], 
                                                    'n_question': i})
                self.fn_question_list.append(single_question)
                # Preprocessing with Underthesea
                self.question_list_2[i] = word_tokenize(self.question_list[i], format="text")
                vi_single_question = Document(page_content=self.question_list_2[i],
                                        metadata={'answer': self.ans_list[i], 
                                                    'n_question': i})
                self.vi_processed_question_list.append(vi_single_question)

        def upload_qdrant(self, docs, collection_name):
            #Upload Documents to Qdrant Online Storage
            Qdrant.from_documents(docs,
                                self.embeddings, 
                                ids = self.ids,
                                url=self.qdrant_url, 
                                api_key=self.qdrant_api_key, 
                                content_payload_key="page_content",
                                metadata_payload_key="metadata",
                                collection_name=collection_name,
                                )

        def processing(self):
            self.read_file()
            self.langchain_docs()
            self.upload_qdrant(self.fn_question_list, 'faq')
            if lang == 'vi':
                self.upload_qdrant(self.vi_processed_question_list, 'faqVieProcessed')
            print('Uploaded Documents to Qdrant in 2 Collection faq and faqVieProcessed')
    
    FAQdrant(st.session_state.qdrant_url, 
             st.session_state.qdrant_api_key, 
             file_path=f'{FACTS_DB}/multiple_questions_gen.xlsx',
             ).processing()

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
            self.context_docs = []
            self.vi_processed_context_list = []
            self.ids = []
            for i in range(len(self.context_list)):
                self.ids.append(i)
                single_context = Document(page_content=self.context_list[i], 
                                        metadata={'n_context': i})
                self.context_docs.append(single_context)
                
                # Preprocessing with Underthesea
                self.vi_context_list = self.context_list
                self.vi_context_list[i] = word_tokenize(self.vi_context_list[i], format="text")
                vi_single_context = Document(page_content=self.vi_context_list[i], 
                                        metadata={'n_context': i})
                self.vi_processed_context_list.append(vi_single_context)
            
        def upload_qdrant(self, docs, collection_name):
            #Upload Documents to Qdrant Online Storage
            Qdrant.from_documents(docs,
                                self.embeddings, 
                                ids = self.ids,
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
            self.upload_qdrant(self.context_docs, 'context')
            if self.lang == 'vi':
                self.upload_qdrant(self.vi_processed_context_list, 'contextVieProcessed')
            print('Uploaded Documents to Qdrant in 2 Collection context and contextVieProcessed')

    DocsQdrant(st.session_state.qdrant_url, 
             st.session_state.qdrant_api_key, 
             context=context,
             lang=lang).processing()

    pass
