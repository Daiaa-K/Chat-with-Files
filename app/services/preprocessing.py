import time
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader, WikipediaLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone.vectorstores import Pinecone
import pinecone
from utils.logger import logger
from config.settings import settings
from langchain_huggingface import HuggingFaceEmbeddings
from huggingface_hub import login


class Preprocessing:
    """
    A class to handle preprocessing of documents.
    """
    def __init__(self, file_path: str):
        self.embedding_model_name = settings.EMBEDDING_MODEL_NAME
        self.index_name = settings.INDEX_NAME
        self.file_path = file_path
        self.pc = pinecone.Pinecone(api_key=settings.PINECONE_KEY)
        login(token=settings.HF_TOKEN)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={"device": "cpu"}
        )

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
            )
            
            chunks = text_splitter.split_documents(docs)
            logger.info(f"Chunked documents into {len(chunks)} pieces.")
            return chunks
        except Exception as e:
            logger.error(f"Error chunking documents: {e}")
            raise e    
        
    def create_embeddings_pinecone(self,chunks):
        """
        Create embeddings for the document chunks and store them in Pinecone.
        Args:
            chunks (List[Document]): List of document chunks to create embeddings for.
        """
        try:

            
            logger.info("Testing embeddings...")
            emb = self.embeddings.embed_query("hello world")
            logger.info(f"Sample embedding vector (first 5 values): {emb[:5]}")
            
            if self.index_name in self.pc.list_indexes().names():
                self.pc.delete_index(self.index_name)
                logger.info(f"Deleted existing Pinecone index: {self.index_name}")

            self.pc.create_index(
                name=self.index_name,
                dimension=len(emb),
                metric="cosine",
                spec=pinecone.ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
        ) 
            )
            logger.info(f"Created Pinecone index: {self.index_name}")
            
            logger.info("Creating embeddings using HuggingFaceEmbeddings.")
            vector_store = Pinecone.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                index_name=self.index_name
            )
            logger.info(f"Created embeddings and stored in Pinecone index: {self.index_name}")
            #  Get vector count from Pinecone stats
            index = self.pc.Index(self.index_name)
            stats = index.describe_index_stats()

            time.sleep(5)  # Wait for a few seconds to ensure stats are updated
            logger.info(f"Index stats: {stats}")
            return vector_store
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise e
        
    def load_embeddings_pinecone(self):
        """Load existing Pinecone embeddings from the specified directory.
        
        Returns:
            VectorStore: The vector store containing the embeddings.
        """
        try:
            # Check if the directory exists
            if not self.index_name in self.pc.list_indexes().names():
                print(f"index {self.index_name} does not exist.")
                return None
            vector_store = Pinecone.from_existing_index(
                embedding=self.embeddings,
                index_name=self.index_name
            )
            logger.info(f"loaded embeddings from Pinecone index: {self.index_name}")
            return vector_store
        except Exception as e:
            logger.error(f"Error loading embeddings: {e}")
            raise e
        
    def preprocess(self):
        """Complete preprocessing pipeline: load document, chunk it, and create/load embeddings.
        
        Returns:
            VectorStore: The vector store containing the embeddings.
        """
        try:
                docs = self.load_doc()
                chunks = self.chunk_docs(docs)
                vector_store = self.create_embeddings_pinecone(chunks)
                return vector_store
        except Exception as e:
            logger.error(f"Error in preprocessing pipeline: {e}")
            raise e