# config.py for Game of Thrones Neo4j Chatbot

DELETE_QUERIES = [
    "MATCH (:Character)-[r:ALLIED_WITH]->(:House) DELETE r",
    "MATCH (:Character)-[r:MEMBER_OF]->(:House) DELETE r",
    "MATCH (:Location)-[r:PART_OF]->(:Region) DELETE r",
    "MATCH (:Character)-[r:RULES]->(:Location) DELETE r",
    "MATCH (:Character)-[r:OWNS]->(:Item) DELETE r"
]

ALLOWED_NODES = [
    'Character', 'House', 'Location', 'Region', 'Item', 'Event', 
    'Creature', 'Organization', 'Weapon', 'Title'
]

ALLOWED_RELATIONSHIPS = [
    'ALLIED_WITH', 'MEMBER_OF', 'PART_OF', 'RULES', 'OWNS',
    'PARTICIPATED_IN', 'KILLED', 'PARENT_OF', 'MARRIED_TO',
    'SWORN_TO', 'LOCATED_IN', 'WIELDS', 'HOLDS_TITLE'
]

RELATIONSHIP_PROPERTIES = [
    'start_date', 'end_date', 'strength', 'type', 'details'
]

NODE_PROPERTIES = [
    'name', 'birth_date', 'death_date', 'gender', 'description',
    'allegiance', 'culture', 'titles', 'aliases'
]