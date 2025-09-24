from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.memory import ConversationBufferMemory, FileChatMessageHistory
from langchain.chains import ConversationalRetrievalChain
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.logger import logger
from config.settings import settings
from utils.utility_functions import clean_up_sessions
import os
import uuid

class ConversationAnswering:
    """_summary_
    A class to handle conversational question answering using a language model and a vector store.
    """
    
    def __init__(self,vector_store, question:str,k=5, conversation= None):
        self.vector_store = vector_store
        self.question = question
        self.k = k
        self.conversation = conversation
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE,
            max_output_tokens=settings.MAX_TOKENS
        )
        self.temperature = settings.TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
        self.session_id = str(uuid.uuid4())
        
    def conversation_answer(self):
        """
        Generate an answer to the user's question based on the conversation history and relevant documents from the vector store.
        
        """
        try:
            if self.conversation is None:
                # define prompt 
                prompt = ChatPromptTemplate(
                    input_variables=["question", "context"],
                    messages = [
                        SystemMessage(content="""you are a helpful assistant that helps
                            people find information from the provided context,
                            answer as truthfully as possible using the provided context,
                            if you don't know the answer, just say "The provided context does not
                            contain this specific information." """),
                        MessagesPlaceholder(variable_name="chat_history"),
                        HumanMessagePromptTemplate.from_template(
                            """
                            Answer the question based only on the following context:
                            {context}
                            
                            Question:{question}
                            
                            provide a precise and concise answer. if the question is not related to the context,
                            politely respond that you are tuned to only answer questions that are related to the context,
                            and if the information is not present in the context, say "The provided context does not
                            contain this specific information."
                            """
                        )
                        
                    ]
                )
            retriever = self.vector_store.as_retriever(search_type="similarity", search_kwargs={"k": self.k})

            clean_up_sessions(settings.HISTORY_DIR, max_sessions=10)
            history = FileChatMessageHistory(
                file_path=os.path.join(settings.HISTORY_DIR,f"chat_history_{self.session_id}.json")
                )
            
            memory = ConversationBufferMemory(
                memory_key="chat_history", 
                return_messages=True,
                chat_memory=history
            )
            chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=memory,
                combine_docs_chain_kwargs={"prompt": prompt},
                return_source_documents=True
            )
            
            self.conversation = {
                "chain":chain,
                "memory":memory
            }
            logger.info(f"Question: {self.question}")
            answer = self.conversation["chain"].invoke({"question": self.question})
            logger.info(f"Answer: {answer}")
            
            return answer, self.session_id
        except Exception as e:
            logger.error(f"Error in conversation answering: {e}")
            raise e