import vertexai
from vertexai.preview.language_models import TextGenerationModel
from google.cloud import translate
from langchain.vectorstores import Chroma
from langchain.embeddings import CohereEmbeddings
from underthesea import word_tokenize
from qdrant_client import QdrantClient
from langchain.vectorstores import Qdrant
import openai
import os
import streamlit as st
from datetime import datetime

class BookQA:
    def __init__(self, 
                 vector_path:str='vectordb', 
                 collection_name:str=None,
                 query:str=None, #Put some questions / queries here
                 llm:str='chatgpt', #Or 'palm2'
                 vmethod:str='chroma',
                 book_lang:str='en',
                 top_k_searching:int=5,
                 ):
        
        self.vector_path = vector_path
        self.collection_name = collection_name
        self.vmethod = vmethod
        # self.query = query
        self.llm = llm
        self.book_lang = book_lang
        self.top_k_searching = top_k_searching
        
        self.qdrant_url = "https://cd6b8c5a-501f-4449-b488-ea45d252239c.us-east-1-0.aws.cloud.qdrant.io:6333"
        self.qdrant_api_key = "arMcul7YcGwzI9AzmsvA8td7OjV1B2e2DjYl-5cfs0XgCpSx8mwY3w"
        self.embeddings = CohereEmbeddings(model="multilingual-22-12", cohere_api_key="4ECOTqDXJpIYhxMQhUZxY12PPSqvgtYFclJm4Gnz")
        
        openai_api_key = "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"
        openai.api_key = openai_api_key
        os.environ['OPENAI_API_KEY'] = openai_api_key
        self.database_loading()
    
    def bookQnA(self, question):
        self.query = question
        self.searching()

        self.prompting()

        if self.llm == 'palm2':
            # print('Google Responding...\n')
            llm_answer, response_time = self.responding_google()
        else:
            # print('OpenAI Responding...\n')
            llm_answer, response_time = self.responding_openai()

        # print(f'Question: {self.query}\n')
        # print(f'Answer: {llm_answer}')
        # print(f'Response Time: {response_time}\n')

        self.references()

        return llm_answer, response_time
        
    #DATABASE-LOADING------------------------------------------------------------
    def database_loading(self):
        if self.vmethod == 'qdrant':
            self.vectordb_loading()
        elif self.vmethod == 'chroma':
            self.chroma_loading()
        else:
            print("Please select vectordatabase method: 'qdrant' or 'chroma'")
            
    def vectordb_loading(self):
        if "vdatabase" in globals() or "qdrant" in locals():
            del self.vdatabase
        if os.path.exists(self.vector_path):
            [os.remove(os.path.join(root, filename)) for root, dirs, files in os.walk(self.vector_path) \
                                                    for filename in files if filename.endswith(".lock")]

        client = QdrantClient(path=self.vector_path, prefer_grpc=True)
        self.vdatabase = Qdrant(client=client, collection_name=self.collection_name, embeddings=self.embeddings)
        # print("Qdrant Database loaded from local storage\n")
        
    def chroma_loading(self):
        self.vdatabase = Chroma(persist_directory=self.vector_path, embedding_function=self.embeddings)
        # print("Chroma Database loaded from local storage\n")


    #DATABASE-SEARCHING----------------------------------------------------------
    def searching(self):
        if self.book_lang == 'vi':
            _query = word_tokenize(self.query, format="text")
        else:
            _query = self.query
        self.search_results = self.vdatabase.similarity_search_with_score(_query, k=self.top_k_searching)
        print(f'Finished Search\nTop k = {len(self.search_results)}\n')
        return self.search_results

    def references(self):
        #Return the references
        print("\n")
        try:
            for i in range(len(self.search_results)):
                _pdf_name = self.search_results[i][0].metadata["source"].split("/")[-1]
                _ref_page = self.search_results[i][0].metadata["page"]
                print(f"Reference {i+1}: Page {_ref_page} in the file {_pdf_name}")
        except KeyError:
            # print("No References from this document\n")
            pass
    #PROMPTING-------------------------------------------------------------------
    def prompting(self):
        # Merge all search results into prompt
        _search_info = " --- " + " --- ".join([self.search_results[i][0].page_content 
                                for i in range(len(self.search_results))]) + " --- "
        #Translate to EN if using Palm2-----------------------------------
        if self.llm == 'palm2' and self.book_lang == 'vi':
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'assets/credential/ambient-hulling-389607-89c372b7af63.json'
            self.PARENT = f"projects/{'ambient-hulling-389607'}"
            #---VI-EN_TRANSLATION----------------------------------------
            _search_info = _search_info.replace("_"," ")
            translated_search_info = self.translate_text(_search_info, target_language_code='en')
            _search_info = translated_search_info.translated_text

        self.prompt = f"""
        You will be provided with the question which is delimited by XML tags and the \
        context delimited by triple backticks. 
        The context contains 5 long paragraphs which delimited by triple dash. \
        <tag>{self.query}</tag>
        ````{_search_info}```
        """
        # Follow the below steps to find the answer for the question:
        # If the long paragraph has a structure of a Menu page, lets ignore this paragraph.

        # Step 1 - Separate the context into 5 single paragraphs delimited by triple dash. 
        # Step 2 - Based on the topic of the question, let's sumaries each paragraph. 
        # Step 3 - Base on 5 sumarizations, give the final answer for the question.
        # Step 4 - Show only the final answer.

        # Let's process Step 1, 2, 3 in silence, only push step 4 to response.

        if self.book_lang=='vi':
            self.prompt = self.prompt.replace("_"," ")
        
        # print('Finished Prompting\n')
                    
    def tiktoken_len(self, text):
        import tiktoken
        tokenizer = tiktoken.get_encoding('cl100k_base')
        tokens = tokenizer.encode(
            text,
            disallowed_special=()
        )
        return len(tokens)
    
    #CHATPGT-RESPONSES-----------------------------------------------------------
    def responding_openai(self):
        prompt_token_length = self.tiktoken_len(self.prompt)
        if prompt_token_length > 16000:
            print("Length of Prompt exceeds the limitation of LLM input. Task closed!")
        else:    
            _start = datetime.now()
            if self.book_lang == 'vi':
                _sys_messages = [{"role": "system", "content": "You are a helpful assistant that gives a comprehensive answer  \
                                in Vietnamese from the given information"},
                                {"role": "user", "content": self.prompt}]
            else:
                _sys_messages = [{"role": "system", "content": "You are a helpful assistant that gives a comprehensive answer  \
                                from the given information"},
                                {"role": "user", "content": self.prompt}]
            response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-16k",
                    messages=_sys_messages,
                    max_tokens = 16000 - prompt_token_length, #Maximum length of tokens is 4096 included Prompt Tokens
                    n=1,
                    temperature=0.1,
                    top_p=0.7,
                )
            self.results = response.choices[0].message.content
            self.chatgpt_tokens = response.usage.total_tokens
            #Response Time (s)
            self.chatgpt_response_time = (datetime.now() - _start)
            
        return self.results, self.chatgpt_response_time
        
    
    #GOOGLE-RESPONSES------------------------------------------------------------
    def responding_google(self):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'assets/credential/ambient-hulling-389607-89c372b7af63.json'
        self.PARENT = f"projects/{'ambient-hulling-389607'}"
        #---VI-EN_TRANSLATION----------------------------------------
        # self.prompt = self.translate_text(self.prompt, target_language_code='en')
        # print(f"{self.prompt.translated_text}")

        #---PALM2-RESPONSE-------------------------------------------
        en_response = self.palm_response(self.prompt)
        # print(en_response)
        if self.book_lang == 'vi':
            #---EN-VI_TRANSLATION----------------------------------------
            vi_response = self.translate_text(en_response, target_language_code='vi')
            return vi_response.translated_text, self.palm2_response_time
        else:
            return en_response, self.palm2_response_time
        #---TRANSLATION----------------------------------------------
    def translate_text(self, text: str, target_language_code: str) -> translate.Translation:
        client = translate.TranslationServiceClient()

        response = client.translate_text(
            parent=self.PARENT,
            contents=[text],
            target_language_code=target_language_code,
            )
        return response.translations[0]

    #---PALM2-RESPONSE-----------------------------------------------
    def predict_large_language_model_gg(self,
                                            project_id: str,
                                            model_name: str,
                                            temperature: float,
                                            max_decode_steps: int,
                                            top_p: float,
                                            top_k: int,
                                            content: str,
                                            location: str = "us-central1",
                                            tuned_model_name: str = "",
                                            ):
        """Predict using a Large Language Model."""
        vertexai.init(project=project_id, location=location)

        model = TextGenerationModel.from_pretrained(model_name)

        if tuned_model_name:
            model = model.get_tuned_model(tuned_model_name)

        response = model.predict(
                                content,
                                temperature=temperature,
                                max_output_tokens=max_decode_steps,
                                top_k=top_k,
                                top_p=top_p,)
        return response.text

    def palm_response(self, content):
        _start = datetime.now()
        res = self.predict_large_language_model_gg(project_id="ambient-hulling-389607", 
                                                    model_name="text-bison@001", 
                                                    temperature=0.1, 
                                                    max_decode_steps=1024, 
                                                    top_p=0.8, 
                                                    top_k=40, 
                                                    content=content,
                                                    location = "us-central1",
                                                    )
        # print(textwrap.fill(res, width=100))
        self.palm2_response_time = datetime.now() - _start
        return res