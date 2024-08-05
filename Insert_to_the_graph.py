import getpass
import os
import json
import glob
import traceback

from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from graph import driver
from config import ALLOWED_NODES, ALLOWED_RELATIONSHIPS, RELATIONSHIP_PROPERTIES, NODE_PROPERTIES
from langchain_core.documents import Document
from PyPDF2 import PdfReader
from neo4j.exceptions import ServiceUnavailable, AuthError

from llm import OpenAIEmbedding

PATH = 'books'
gpt4o = ChatOpenAI(temperature=0, model_name="gpt-4o")
llm_embedder = OpenAIEmbedding(model='text-embedding-3-small')

def dump_graph(graph_documents_props, driver: Neo4jGraph):
    try:
        driver.add_graph_documents(
            graph_documents_props, 
            baseEntityLabel=True, 
            include_source=True
        )
        print('Graph dumped successfully')
    except ServiceUnavailable:
        print("Failed to connect to Neo4j database. Please check if the database is running and accessible.")
    except AuthError:
        print("Authentication failed. Please check your Neo4j credentials.")
    except Exception as e:
        print(f"An error occurred while dumping the graph: {str(e)}")

def full_book_construction(path, starting_page=0, ending_page=None):
    try:
        book = PdfReader(path)
        if ending_page is None:
            ending_page = len(book.pages)
        full_book = ''
        for i in range(starting_page, ending_page):
            page = book.pages[i].extract_text().replace('\t', ' ').replace('https://www.8freebooks.net', ' ')
            full_book = full_book + page + ' '
        return full_book
    except Exception as e:
        print(f"Error in full_book_construction: {str(e)}")
        return None

from langchain.text_splitter import RecursiveCharacterTextSplitter

def documents_constructor(full_book):
    if not full_book:
        return []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200
    )
    docs = [Document(page_content=doc) for doc in text_splitter.split_text(full_book)]
    print(f"Created {len(docs)} documents")
    return docs

def generate_prompt(doc_content):
    prompt_template = """
    Generate nodes and relationships for the following Game of Thrones related document:
    
    Node instructions:
    1. Create nodes for characters, houses, locations, regions, items, events, creatures, organizations, weapons, and titles that appear in the text.
    2. Make sure all created nodes are part of the allowed node types.
    3. For each node, provide relevant properties such as name, birth_date, death_date, gender, description, allegiance, culture, titles, and aliases where applicable.

    Relationship instructions:
    1. Use ALLIED_WITH for alliances between characters or houses.
    2. Use MEMBER_OF to show a character's membership in a house or organization.
    3. Use PART_OF to indicate a location being part of a larger region.
    4. Use RULES to show a character's rulership over a location.
    5. Use OWNS to indicate possession of items or weapons by characters.
    6. Use PARTICIPATED_IN to link characters to events.
    7. Use KILLED for instances where one character killed another.
    8. Use PARENT_OF to establish family relationships.
    9. Use MARRIED_TO for marriages between characters.
    10. Use SWORN_TO for oaths of loyalty.
    11. Use LOCATED_IN to place characters or items in specific locations.
    12. Use WIELDS for characters using specific weapons.
    13. Use HOLDS_TITLE to associate characters with their titles.

    Relationship property instructions:
    1. Include start_date and end_date for time-bound relationships.
    2. Use strength to indicate the power of alliances or other relationships.
    3. Specify type for further categorization of relationships.
    4. Provide details for additional context about the relationship.

    Document:
    {doc_content}

    Allowed nodes: {allowed_nodes}
    Allowed relationships: {allowed_relationships}
    Relationship properties: {relationship_properties}
    Node properties: {node_properties}
    """
    return prompt_template.format(
        doc_content=doc_content,
        allowed_nodes=','.join(ALLOWED_NODES),
        allowed_relationships=','.join(ALLOWED_RELATIONSHIPS),
        relationship_properties=','.join(RELATIONSHIP_PROPERTIES),
        node_properties=','.join(NODE_PROPERTIES)
    )

graph_dict = {}
pdf_files = glob.glob(os.path.join(PATH, "*.pdf"))
documents_dict = {}

for path in pdf_files:
    print(f"Processing file: {path}")
    text = full_book_construction(path=path, starting_page=300, ending_page=320)
    if text:
        documents = documents_constructor(text)
        documents_dict[path] = documents
    else:
        print(f"Skipping file {path} due to error in text extraction")

i = 1
for doc_name, documents in documents_dict.items():
    for doc in documents:
        try:
            print(f"Processing document {i} from {doc_name}")
            prompt_callable = lambda doc_content=doc.page_content: generate_prompt(doc_content)
            llm_transformer_props = LLMGraphTransformer(
                llm=gpt4o,
                allowed_nodes=ALLOWED_NODES,
                allowed_relationships=ALLOWED_RELATIONSHIPS,
                relationship_properties=RELATIONSHIP_PROPERTIES,
                node_properties=NODE_PROPERTIES,
                prompt=prompt_callable
            )

            graph_documents_props = llm_transformer_props.convert_to_graph_documents([doc])
            
            try:
                embedding = llm_embedder(doc.page_content)
                graph_documents_props[0].source.metadata['embedding'] = embedding.tolist()  # Convert numpy array to list
            except Exception as e:
                print(f"Error creating embedding: {str(e)}")
                print("Skipping embedding for this document")
            
            graph_documents_props[0].source.metadata['chunk_number'] = i
            graph_documents_props[0].source.metadata['doc_name'] = doc_name

            graph_dict[i] = graph_documents_props[0].dict()
            print(f"Nodes: {graph_documents_props[0].nodes}")
            print(f"Relationships: {graph_documents_props[0].relationships}")

            dump_graph(graph_documents_props, driver)

            if i % 10 == 0:
                with open('graph_dict.json', 'w', encoding='utf-8') as f:
                    json.dump(graph_dict, f, ensure_ascii=False, indent=4)
            
            i += 1

        except Exception as e:
            print(f"Error processing document {i} from {doc_name}: {str(e)}")
            traceback.print_exc()
            continue

    print(f"Finished processing all documents from {doc_name}")

with open('graph_dict.json', 'w', encoding='utf-8') as f:
    json.dump(graph_dict, f, ensure_ascii=False, indent=4)

print("Script completed successfully")