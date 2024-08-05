import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm import got_chat_model as chat_model, langchain_embeddings
from graph import driver
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

def create_vector_index(driver):
    # This function creates a new vector index if it doesn't exist
    # Adjust the Cypher query based on your specific needs and database structure
    query = """
    CALL db.index.vector.createNodeIndex(
      'got_doc_embedding',
      'GoTDocument',
      'embedding',
      1536,
      'cosine'
    )
    """
    driver.query(query)

try:
    neo4jvector = Neo4jVector.from_existing_index(
        langchain_embeddings,
        graph=driver,
        index_name="got_doc_embedding",
        node_label="GoTDocument",
        text_node_property="text",
        embedding_node_property="embedding",
        retrieval_query="""
        RETURN
         node.text AS text,
         score,
         {
         doc_id: node.chunk_number,
         MENTIONS: [ (node)-[:MENTIONS]->(entity) | [entity.name, entity.type] ]
         } AS metadata
        """
    )
except ValueError as e:
    print(f"Error: {e}")
    print("Attempting to create the vector index...")
    create_vector_index(driver)
    # Try to create the Neo4jVector again after creating the index
    neo4jvector = Neo4jVector.from_existing_index(
        langchain_embeddings,
        graph=driver,
        index_name="got_doc_embedding",
        node_label="GoTDocument",
        text_node_property="text",
        embedding_node_property="embedding",
        retrieval_query="""
        RETURN
         node.text AS text,
         score,
         {
         doc_id: node.chunk_number,
         MENTIONS: [ (node)-[:MENTIONS]->(entity) | [entity.name, entity.type] ]
         } AS metadata
        """
    )

retriever = neo4jvector.as_retriever()

instructions = (
    "You are a knowledgeable maester of the Citadel. Use the given context to answer questions about the world of Game of Thrones. "
    "If you don't know the answer, say you don't know and offer to consult the ancient texts for more information. "
    "Context: {context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", instructions),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(chat_model, prompt)

text_retriever = create_retrieval_chain(
    retriever,
    question_answer_chain
)

def get_got_text(input):
    return text_retriever.invoke({"input": input})

# Example usage
if __name__ == "__main__":
    answer = get_got_text("Tell me about the history of House Targaryen")
    print(answer)