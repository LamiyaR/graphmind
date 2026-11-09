#to run the loader.py we created in graphmind where we added paper to db, now we need to execute it
from graphmind.ingest.loader import load_papers


if __name__ == "__main__":
    load_papers()