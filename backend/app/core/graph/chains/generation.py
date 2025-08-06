from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
from ...models.model import get_chat_model

llm = get_chat_model()

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI assistant specialized in answering questions using provided context documents.

Instructions:
- Use the provided context to answer the question accurately and comprehensively
- IMPORTANT: Include the actual information, details, and explanations from the context in your answer
- Do NOT just reference that information exists in the documents - actually provide the information
- Be specific and detailed in your response, including examples, methods, or approaches mentioned in the context
- If the context mentions specific techniques, list them out explicitly
- If the question cannot be answered from the context, say so explicitly

Context Documents:
{context}"""),
    ("human", "Question: {question}")
])

generation_chain: RunnableSequence = rag_prompt | llm | StrOutputParser()
