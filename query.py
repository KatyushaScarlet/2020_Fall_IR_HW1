import sys
import os
import math

from warc.parser import Parser
from indexing.index import Index


def usage():
    print("Usage:")
    print("\tpython3", sys.argv[0], "[-r number] -w warc_file_name -q free_query_text")
    print("\tpython3", sys.argv[0], "-h")
    print("\r\nParameter:")
    print("\t", "-r\t", "WARC file, can auto detect index file is exist or not.")
    print("\t", "-r\t", "control that how many document may display. default is 10")
    print("\t", "-q\t", "free text query term")
    print("\t", "-h\t", "show this helper")
    print("\r\nExample:")
    print("python3", sys.argv[0], "-w 00.warc", "-q hong kong")
    exit(0)


def query():
    file_name = ""
    return_count = 10
    N = 0

    # parse parameters
    if len(sys.argv) >= 3:
        if "-w" in sys.argv:
            file_name = sys.argv[sys.argv.index("-w") + 1]
        else:
            usage()
        if "-r" in sys.argv:
            return_count = int(sys.argv[sys.argv.index("-r") + 1])

        if "-q" in sys.argv:
            query_string = sys.argv[sys.argv.index("-q") + 1:]
        else:
            usage()
    else:
        usage()

    # set idx file and dict file path
    idx_file = file_name + "_index.idx"
    dict_file = file_name + "_index.dict"

    # error detection
    if not os.path.isfile(idx_file) or not os.path.isfile(idx_file):
        print("Error: index dictionary file(_index.dict or inverted index file (_index.idx) not found.",
              file=sys.stderr)
        exit(1)


    # count total document N
    parser = Parser(file_name)
    while True:
        if parser.fetch() is not None:
            N += 1
        else:
            break

    # read dict file to dict
    dict_file = open(dict_file)
    dicts = {}
    for d in dict_file:
        (key, offset) = d.split(', ')
        dicts[key] = int(offset)

    # term's index
    term_index = {}
    # query's parameter table
    query_table = {}
    # docs's parameter table
    docs_table = {}
    # docs set for merge document
    docs_set = set()
    # docs score hash, use cosine similarity score with weight use tf-idf
    docs_score = {}
    # Calculate query's weight
    for term in query_string:
        if term in dicts:
            term_index[term] = Index.read_index_by_offset(idx_file, dicts[term]).index[term]
            # add doc# to set
            for doc in term_index[term]:
                docs_set.add(int(doc))
            query_table[term] = {}
            query_table[term]["tf"] = 1
            query_table[term]["df"] = len(term_index[term])
            query_table[term]["idf"] = math.log(N / query_table[term]["df"], 10)
            query_table[term]["w"] = (1 + math.log(query_table[term]["tf"])) * query_table[term]["idf"]
        else:
            term_index[term] = {}
            query_table[term] = {}
            query_table[term]["tf"] = 1
            query_table[term]["df"] = 0
            query_table[term]["idf"] = 0
            query_table[term]["w"] = 0

    # Calculate query's weight
    euclidean_length = 0
    while True:
        try:
            element = str(docs_set.pop())
        except KeyError:
            break
        docs_table[element] = {}
        for term in query_string:
            docs_table[element][term] = {}
            docs_table[element][term]["tf"] = 0
            if element in term_index[term]:
                docs_table[element][term]["tf"] = len(term_index[term][str(element)])
            euclidean_length += docs_table[element][term]["tf"] * docs_table[element][term]["tf"]
    euclidean_length = math.sqrt(euclidean_length)

    for doc in docs_table:
        for term in query_string:
            if docs_table[doc][term]["tf"] > 0:
                docs_table[doc][term]["w"] = (1 + math.log(docs_table[doc][term]["tf"], 10)) * math.log(
                    query_table[term]["df"], 10)
            else:
                docs_table[doc][term]["w"] = 0

    query_len = 0
    for term in query_string:
        query_len += query_table[term]["w"] * query_table[term]["w"]
    query_len = math.sqrt(query_len)

    for doc in docs_table:
        up_part = 0
        doc_len = 0
        for terms in query_string:
            up_part += docs_table[doc][terms]["w"] * query_table[terms]["w"]
            doc_len += docs_table[doc][terms]["w"] * docs_table[doc][terms]["w"]
        docs_score[doc] = up_part / (math.sqrt(doc_len) * query_len)

    print("Query terms:", query_string)
    print("Top", return_count, "results:")
    print("doc#\tscore")

    for i in sorted(docs_score, key=docs_score.get, reverse=True):
        return_count -= 1
        if return_count < 0:
            break
        print("%d\t%.3f" % (int(i), docs_score[i]))


if __name__ == "__main__":
    if "-h" in sys.argv:
        usage()
    elif "-q" in sys.argv:
        query()
    else:
        usage()
