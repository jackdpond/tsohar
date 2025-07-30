from scribe import Index
import argparse

def search():
    parser = argparse.ArgumentParser()
    parser.add_argument('search', type=str, help='String to search')
    parser.add_argument('-k', '--k_nearest_neighbors', type=int, default=5, help='How many of the nearest results to print out')
    parser.add_argument('-f', '--filename', default='database/bp_db', help='Path to the Vector Database files')
    args = parser.parse_args()

    index = Index()
    index.load_database(args.filename)

    return index.search(args.search, args.k_nearest_neighbors, verbose=True)

if __name__ == "__main__":
    search()