import os
from langchain.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader, WikipediaLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from utils.logger import logger
from config.settings import settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class Preprocessing:
    """
    A class to handle preprocessing of documents.
    """
    def __init__(self, file_path: str):
        self.embedding_model_name = settings.EMBEDDING_MODEL_NAME
        self.db_dir = os.path.join(settings.DATABASE_DIR, "chroma_db")
        self.file_path = file_path

    def load_doc(self):
        """Load a document from the specified file path.
        """
        
        try:
            if self.file_path.endswith(".pdf"):
                loader = PyPDFLoader(self.file_path)
            elif self.file_path.endswith(".txt"):
                loader = TextLoader(self.file_path, encoding='utf-8')
            elif self.file_path.endswith(".docx"):
                loader = Docx2txtLoader(self.file_path)
            else:
                logger.error("Unsupported file format. Supported formats are: .pdf, .txt, .docx")
                raise ValueError("Unsupported file format.")
            
            docs = loader.load()
            logger.info(f"Loaded document from {self.file_path}")
            return docs
        except FileNotFoundError:
            logger.error(f"File not found: {self.file_path}")
            raise
        except PermissionError:
            logger.error(f"Permission denied when accessing the file: {self.file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading document: {e}")
            raise e
        
    def load_from_wiki(self, query, lang="en", load_max_docs=2):
        """Load content from Wikipedia based on a query.
        
        Args:
            query (str): The search term to look up on Wikipedia.
            lang (str, optional): Language code for Wikipedia. Defaults to "en".
            load_max_docs (int, optional): Maximum number of documents to load. Defaults to 2.
        """
        try:
            loader = WikipediaLoader(query=query, lang=lang, load_max_docs=load_max_docs)
            docs = loader.load()
            logger.info(f"Loaded {len(docs)} documents from Wikipedia for query: {query}")
            return docs
        except Exception as e:
            logger.error(f"Error loading from Wikipedia: {e}")
            raise e
        
    def chunk_docs(self, docs, chunk_size=512,chunk_overlap = 50):
        """
        Chunk the loaded documents into smaller pieces for processing.
        Args:
            docs (List[Document]): List of documents to be chunked.
            chunk_size (int, optional): Size of each chunk. Defaults to 512.
            chunk_overlap (int, optional): Overlap between chunks. Defaults to 50.
        """
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len
            )
            
            chunks = text_splitter.split_documents(docs)
            logger.info(f"Chunked documents into {len(chunks)} pieces.")
            return chunks
        except Exception as e:
            logger.error(f"Error chunking documents: {e}")
            raise e    
        
    def create_embeddings_chroma(self,docs):
        """_summary_

        Args:
            docs (_type_): _description_
            persist_directory (str, optional): _description_. Defaults to "database/chroma_db".
        """
        try:
            embeddings = GoogleGenerativeAIEmbeddings(
                model = self.embedding_model_name
            )
            
            vector_store = Chroma.from_documents(
                docs,
                embeddings,
                persist_directory=self.db_dir,
            )
            logger.info(f"Created embeddings and stored in ChromaDB at {self.db_dir}")
            vector_store.persist()
            return vector_store
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise e
        
    def load_embeddings_chroma(self):
        """Load existing ChromaDB embeddings from the specified directory.
        
        Returns:
            Chroma: The loaded Chroma vector store.
        """
        try:
            embeddings = GoogleGenerativeAIEmbeddings(
                model = self.embedding_model_name
            )
            vector_store = Chroma(
                persist_directory=self.db_dir,
                embedding_function=embeddings
            )
            logger.info(f"Loaded embeddings from ChromaDB at {self.db_dir}")
            return vector_store
        except Exception as e:
            logger.error(f"Error loading embeddings: {e}")
            raise e
        
    def preprocess(self):
        """Complete preprocessing pipeline: load document, chunk it, and create/load embeddings.
        
        Returns:
            Chroma: The Chroma vector store with embeddings.
        """
        try:
            if not os.path.exists(self.db_dir) or not os.listdir(self.db_dir):
                docs = self.load_doc()
                chunks = self.chunk_docs(docs)
                vector_store = self.create_embeddings_chroma(chunks)
            else:
                vector_store = self.load_embeddings_chroma()
            return vector_store
        except Exception as e:
            logger.error(f"Error in preprocessing pipeline: {e}")
            raise e