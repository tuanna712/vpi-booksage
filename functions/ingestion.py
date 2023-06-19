import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sb
import tiktoken

from langchain.document_loaders import Docx2txtLoader
from langchain.document_loaders import PyPDFLoader

from underthesea import sent_tokenize
from underthesea import word_tokenize

from langchain.chains.question_answering import load_qa_chain

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from langchain.embeddings import CohereEmbeddings

from langchain.vectorstores import Chroma
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient


