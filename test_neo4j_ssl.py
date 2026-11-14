import truststore

truststore.inject_into_ssl()

from graphmind.db.neo4j_client import connect_neo4j

driver = connect_neo4j()

try:
    driver.verify_connectivity()
    print("Neo4j connected successfully!")
finally:
    driver.close()