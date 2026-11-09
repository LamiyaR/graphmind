from neo4j import GraphDatabase

from graphmind.config import (
    NEO4J_URI,
    NEO4J_USER,
    NEO4J_PASSWORD
)


def connect_neo4j():
    #driver- bridge between Python and Neo4j
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )

    return driver


def test_connection():

    driver = connect_neo4j()

    try:
        driver.verify_connectivity()

        print("Successfully connected to Neo4j!")

    except Exception as error:

        print("Connection failed:", error)

    finally:
        driver.close()


if __name__ == "__main__":
    test_connection()