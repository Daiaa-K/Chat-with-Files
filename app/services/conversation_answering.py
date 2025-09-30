import uuid
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage
from utils.logger import logger
from config.settings import settings
from utils import history_manager
from langchain.schema import SystemMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from huggingface_hub import login

class ConversationAnswering:
    """
    Service for handling conversational QA with per-session memory,
    persisting each session to a history file.
    """
    sessions = {}  # in-memory: session_id -> ConversationBufferMemory
    
    def __init__(self, vector_store, session_id: str = None):
        self.vector_store = vector_store
        self.session_id = session_id or str(uuid.uuid4())
        QA_PROMPT = ChatPromptTemplate.from_messages([
            SystemMessage(
                """You are an intelligent AI assistant.
                You can use three sources when answering:
                1. The current user's question.
                2. Relevant context retrieved from documents.
                3. The ongoing conversation history.

                - If the user refers to something mentioned earlier,
                resolve it using the conversation history.  
                - Prefer using document context when available.  
                - If the answer cannot be found in either the documents or the conversation history, say "I don't know".  
                - Be clear, concise, and correct. Adjust technical depth based on the question.  
                """
            ),
            HumanMessagePromptTemplate.from_template(
                """Conversation history:
                {chat_history}

                Retrieved context:
                {context}

                Question:
                {question}

                Provide the best possible answer. If uncertain, say "I don't know".
                """
            )
        ])
        

        # If no memory exists for this session, create one
        if self.session_id not in ConversationAnswering.sessions:
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )

            # Load history from file
            past = history_manager.load_history(self.session_id)
            for item in past:
                if item["role"] == "human":
                    memory.chat_memory.add_message(HumanMessage(content=item["content"]))
                elif item["role"] == "ai":
                    memory.chat_memory.add_message(AIMessage(content=item["content"]))

            ConversationAnswering.sessions[self.session_id] = memory

        self.memory = ConversationAnswering.sessions[self.session_id]

        # Build retrieval QA chain
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=ChatGoogleGenerativeAI(
                model=settings.MODEL_NAME,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=settings.TEMPERATURE,
                max_output_tokens=settings.MAX_TOKENS
            ),
            retriever=self.vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5}),
            chain_type="stuff",
            memory=self.memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt":QA_PROMPT}
        )
        

    def conversation_answer(self, question: str):
        """
        Ask a question and get an answer, persisting conversation history.
        """
        logger.info("Starting conversation_answer()")
        logger.info(f"Question: {question}")

        try:
            # Call the chain
            answer = self.chain.invoke({"question": question})
            docs = answer.get("source_documents", [])
            logger.info(f"Retrieved {len(docs)} documents for question")
            
            for i, d in enumerate(docs):
                try:
                    snippet = d.page_content[:100].replace("\n", " ")
                    logger.info(f"Doc {i+1} snippet: {snippet}...")
                except UnicodeEncodeError:
                    logger.info(f"Doc {i+1} snippet: [Error displaying content]")
                
            # Extract answer text
            answer_text = answer.get("result") or answer.get("answer") or str(answer)

            # Update memory
            """try:
                self.memory.chat_memory.add_message(HumanMessage(content=question))
                self.memory.chat_memory.add_message(AIMessage(content=answer_text))
            except Exception as e:
                logger.warning(f"Error updating memory: {e}", exc_info=True) """

            # Save to file
            history_manager.save_history(self.session_id, question, answer_text)

            logger.info(f"Got response: {answer_text}")
            return {"answer": answer_text, "session_id": self.session_id}

        except Exception as e:
            logger.error(f"Error in conversation answering: {e}", exc_info=True)
            return {"answer": "Error while generating response.", "session_id": self.session_id}
