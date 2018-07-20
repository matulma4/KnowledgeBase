import gc
import json
import sqlite3
import sys

import nltk
import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from requests_aws4auth import AWS4Auth
from ld_creator import create_property, create_text, create_headline, create_type

from config import *

blacklist = [line.strip() for line in open("blacklist.txt")]

def query_label_lookup(name):
    r = requests.get(lookup_url + name.replace(" ", "%20"))
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
                if named_entity not in blacklist:
                    continuous_chunk.append(named_entity)
                current_chunk = []
        else:
            continue
    return continuous_chunk


def create_es():
    try:
        keys = open("creds.aws").read().strip().split(" ")
    except FileNotFoundError:
        print("AWS credentials file missing")
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
    s = Search(using=es, index=index)
    s = s.query(query)
    s = s.filter('range', **{'@timestamp': {'gte': 'now-' + time, 'lt': 'now'}})
    s = s.params(scroll='6h')
    return s.scan()


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


def extract_from_gossip(goss):
    result = []
    try:
        result += list(goss.tags)
    except AttributeError:
        pass
    return result


def add_art(art, ent):
    ent.add_article(art)


def add_ff(ff, ent):
    ent.add_funfact(ff)


def add_entities(res, extract_func, mode):
    i = 1
    for article in res:
        R1 = []
        try:
            entities = extract_func(article)

            for p in entities:
                q = web_search(p)['results']
                if len(q) <= 0 or len(q[0]) <= 0:
                    continue
                if mode == "funfact":
                    r1 = create_property(q[0][0]["freebase_id"], article.id)
                    # R1.append(r1)
                else:
                    r1 = create_property(q[0][0]["freebase_id"], article.meta.id)
                R1.append(r1)
            if mode == "funfact":
                f.write("\n".join(R1) + "\n")
                f.write(create_text(article.id, article.text.replace("\"", ""), "Blurb") + "\n")
                f.write(create_type(mode, article.id) + "\n")
            elif mode == "article":
                f.write("\n".join(R1) + "\n")
                f.write(create_headline(article.meta.id, article.headline.replace("\"", "")) + "\n")
                f.write(create_text(article.meta.id, article.blurb.replace("\"", ""), "Blurb") + "\n")
                f.write(create_type(mode, article.meta.id) + "\n")
            else:
                f.write("\n".join(R1) + "\n")
                f.write(create_headline(article.meta.id, article.title.replace("\"", "")) + "\n")
                f.write(create_text(article.meta.id, article.title.replace("\"", ""), "Blurb") + "\n")
                f.write(create_type(mode, article.meta.id) + "\n")
        except AttributeError as e:
            print(e)
            pass
        if i == limit:
            break
        if i % 100 == 0:
            print(i)
        i += 1
        gc.collect()
        f.flush()

    print("Processed " + str(i) + " articles.\n")


def query_es(doctype, bucket, timespan, es):
    q = Q('match', type=doctype)
    return make_search(es, bucket, q, timespan)


def write_to_file(ls):
    with open(rdf_name + ".rdf", "w", encoding="utf-8") as f:  # , open(ent_name + ".rdf", "w", encoding="utf-8") as g:
        for k in ls:
            for article in k.articles:
                r1, r2, r3 = create_property(k.e_id, "article", article.id)
                f.write(r1 + "\n" + r3 + "\n" + r2 + "\n")
            for funfact in k.funfacts:
                r1, r2, r3 = create_property(k.e_id, "funfact", funfact.id)
                f.write(r1 + "\n" + r2 + "\n")


def web_search(name, top_n=3):
    # look for ngram or look just for the whole string
    # db = ""
    result_list = [search(name)]

    # print('looking for:', name)
    # print(result_list)
    # each word has several candidates, so we want to take topn of each
    split_list = [l[:top_n] for l in result_list]
    return {"results": split_list}


def search(name):
    name = name.lower()
    # connection = sqlite3.connect(db)
    # connection.text_factory = str
    with sqlite3.connect(db) as connection:
        cursor = connection.cursor()
        connection.text_factory = str
        cursor.execute(
            "SELECT label, probability, url, freebase_id from labels as l JOIN urls as u on l.url_id = u.id where label=?",
            (name,))
        sresult = cursor.fetchall()
        # print(sresult)
        # TODO: canonLabel? change dist?
        result_list = []
        for r in sresult:
            result = {
                'matchedLabel': r[0],
                'db_id': r[2],
                'freebase_id': r[3],
                'prob': r[1]
            }
            result_list.append(result)
        return result_list


if __name__ == '__main__':
    gc.enable()
    span = sys.argv[1]
    nltk.download('averaged_perceptron_tagger')
    nltk.download('punkt')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')
    es = create_es()
    print(es.info())
    limit = -1

    f = open(rdf_name + ".rdf", "w", encoding="utf-8")
    print("Span is " + span + ", limit is " + str(limit) + ".\n")

    add_entities(query_es("facts", "reddit-*", span, es), extract_from_ff, "funfact")
    add_entities(query_es("article", "washpost_article*", '2d', es), extract_from_art, "article")
    # add_entities(query_es("gossip", "gossip-*", '5y', es), extract_from_gossip, "gossip")
    f.close()
