from graphmind.db.neo4j_client import connect_neo4j
from graphmind.db.schema import CONSTRAINTS


def create_schema():

    driver = connect_neo4j()

    try:
        with driver.session() as session:

            for query in CONSTRAINTS:

                session.run(query).consume()

                print("Constraint created or already exists")

        print("Database schema initialized successfully!")

    finally:
        driver.close()


if __name__ == "__main__":
    create_schema()