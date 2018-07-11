import json
import sys

import nltk
import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from requests_aws4auth import AWS4Auth

from config import *
from ld_creator import create_property, create_text, create_headline


def query_label_lookup(name):
    r = requests.get('http://34.196.128.143:5000/search/' + name.replace(" ", "%20"))
    return json.loads(r.content.decode('utf-8'))


def extract_entities(text):
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    continuous_chunk = []
    current_chunk = []
    for i in chunked:
        if type(i) == Tree:
            current_chunk.append(" ".join([token for token, pos in i.leaves()]))
        elif current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
        else:
            continue
    return continuous_chunk


def create_es():
    try:
        keys = open("creds.aws").read().strip().split(" ")
    except FileNotFoundError:
        print("AWS credenitals file missing")
        sys.exit(1)
    awsauth = AWS4Auth(keys[0], keys[1], "us-east-1", 'es')

    return Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )


def make_search(es, index, query, time):
    return Search(using=es, index=index).query(query).filter('range',
                                                             **{'@timestamp': {'gte': 'now-' + time,
                                                                               'lt': 'now'}}).scan()


def extract_from_ff(ff):
    return extract_entities(ff.text)


def extract_from_art(art):
    result = []
    try:
        result += list(art.person)
    except AttributeError:
        pass
    try:
        result += list(art.organization)
    except AttributeError:
        pass
    try:
        result += list(art.location)
    except AttributeError:
        pass
    return result


def add_art(art, ent):
    ent.add_article(art)


def add_ff(ff, ent):
    ent.add_funfact(ff)


def add_entities(res, extract_func, mode):
    i = 0
    for article in res:
        R1 = []
        R3 = []
        try:
            entities = extract_func(article)

            for p in entities:
                q = query_label_lookup(p)['results']
                if len(q) <= 0 or len(q[0]) <= 0:
                    # i += 1
                    continue
                    # if q[0]["canonLabel"] != p:
                    #     continue
                # if p not in dct.keys():
                #     dct[p] = Entity(p, q[0][0]["freebase_id"])
                # add_func(article, dct[p])
                if mode == "funfact":
                    r1 = create_property(q[0][0]["freebase_id"], mode, article.id)
                    R1.append(r1)
                    # f.write(r1 + "\n")
                else:
                    r1 = create_property(q[0][0]["freebase_id"], mode, article.meta.id)
                    R1.append(r1)
                    # f.write(r1 + "\n" + r3 + "\n")
            if mode == "funfact":
                f.write("\n".join(R1) + "\n")
                f.write(create_text(article.id, article.text, mode) + "\n")
            else:
                f.write("\n".join(R1) + "\n")
                f.write(create_headline(article.meta.id, article.headline, mode) + "\n")
                f.write(create_text(article.meta.id, article.body, mode) + "\n")
        except AttributeError as e:
            print(e)
            pass
        if i == limit:
            break
        # print(i)
        i += 1
        f.flush()

    print("Processed " + str(i) + " articles.\n")
    # return dct


def query_es(doctype, bucket, timespan):
    q = Q('match', type=doctype)
    return make_search(es, bucket, q, timespan)


def write_to_file(ls):
    with open(rdf_name + ".rdf", "w", encoding="utf-8") as f:  # , open(ent_name + ".rdf", "w", encoding="utf-8") as g:
        for k in ls:
            # ent, k_name = create_entity(k)
            for article in k.articles:
                r1, r2, r3 = create_property(article.text, article.headline, k.e_id, "article", article.id)
                f.write(r1 + "\n" + r3 + "\n" + r2 + "\n")
            for funfact in k.funfacts:
                r1, r2, r3 = create_property(funfact.text, None, k.e_id, "funfact", funfact.id)
                f.write(r1 + "\n" + r2 + "\n")
                # g.write(ent + "\n")


if __name__ == '__main__':
    span = '5y'  # sys.argv[1]
    nltk.download('averaged_perceptron_tagger')
    nltk.download('punkt')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')
    es = create_es()
    print(es.info())
    limit = 100

    f = open(rdf_name + ".rdf", "w", encoding="utf-8")
    print("Span is " + span + ", limit is " + str(limit) + ".\n")

    add_entities(query_es("facts", "reddit-*", span), extract_from_ff, "funfact")
    # print("Found " + str(len(dct.keys())) + " entities so far.\n")
    add_entities(query_es("article", "washpost_article*", span), extract_from_art, "article")
    f.close()
    # print("Found " + str(len(dct.keys())) + " entities so far.\n")
    # ent_ls = list(dct.values())
    # write_to_file(ent_ls)
