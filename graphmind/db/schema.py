#In this file we have nodes and edges 
# Names of our node types
PAPER = "Paper"
ENTITY = "Entity"
CHUNK = "Chunk"


# Names of our relationships
MENTIONED_IN = "MENTIONED_IN"
RELATED_TO = "RELATED_TO"
FROM_PAPER = "FROM_PAPER"
MENTIONS = "MENTIONS"


# Database constraints
CONSTRAINTS = [

    """
    CREATE CONSTRAINT paper_pmid IF NOT EXISTS
    FOR (p:Paper)
    REQUIRE p.pmid IS UNIQUE
    """,

    """
    CREATE CONSTRAINT entity_id IF NOT EXISTS
    FOR (e:Entity)
    REQUIRE e.id IS UNIQUE
    """,

    """
    CREATE CONSTRAINT chunk_id IF NOT EXISTS
    FOR (c:Chunk)
    REQUIRE c.id IS UNIQUE
    """

]