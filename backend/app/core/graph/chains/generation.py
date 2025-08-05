from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
from ...models.model import get_chat_model

llm = get_chat_model()

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI assistant specialized in answering questions using provided context documents.

Instructions:
- Use the provided context to answer the question accurately and comprehensively
- If the context doesn't contain enough information, clearly state what information is missing
- Cite relevant parts of the context when possible
- Be concise but thorough in your response
- If the question cannot be answered from the context, say so explicitly

Context Documents:
{context}"""),
    ("human", "Question: {question}")
])

generation_chain: RunnableSequence = rag_prompt | llm | StrOutputParser()
