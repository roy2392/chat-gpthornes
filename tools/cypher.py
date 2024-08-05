import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm import chat_model
from graph import driver
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate

CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer translating user questions into Cypher to answer questions about the world of Game of Thrones.
Convert the user's question based on the schema.
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Do not return entire nodes or embedding properties.

Fine Tuning:
[]

Example Cypher Statements:
1. To find all the characters who are allied with a specific House:
```
MATCH (c:Character)-[r:ALLIED_WITH]->(h:House {{name: 'House name'}})
RETURN c.name, r.details
```
2. To find all the locations that are part of a specific Region:
```
MATCH (l:Location)-[r:PART_OF]->(r:Region {{name: 'Region name'}})
RETURN l.name, r.details
```
3. To find characters who participated in a specific Event:
```
MATCH (c:Character)-[r:PARTICIPATED_IN]->(e:Event {{name: 'Event name'}})
RETURN c.name, r.details
```

Schema:
{schema}

Question:
{question}
"""

cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)

got_cypher_qa = GraphCypherQAChain.from_llm(
    cypher_llm=chat_model,
    graph=driver,
    verbose=True,
    cypher_prompt=cypher_prompt,
    llm=chat_model
)

## example:
# answer = got_cypher_qa(question="Find all the characters who are members of House Stark")
# print(answer)