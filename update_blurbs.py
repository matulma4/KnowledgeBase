from es_search import create_es, query_es
from ld_creator import create_text


def add_entities(res, mode):
    i = 1
    for article in res:
        try:
            if mode == "funfact":
                f.write(create_text(article.id, article.text.replace("\"", ""), "Blurb") + "\n")
            else:
                f.write(create_text(article.meta.id, article.blurb.replace("\"", ""), "Blurb") + "\n")
        except AttributeError as e:
            print(e)
            pass
        if i == limit:
            break
        if i % 100 == 0:
            print(i)
        i += 1
        f.flush()

    print("Processed " + str(i) + " articles.\n")


if __name__ == '__main__':
    span = '5y'
    es = create_es()
    print(es.info())
    limit = -1

    f = open("blurbs.rdf", "w", encoding="utf-8")
    print("Span is " + span + ", limit is " + str(limit) + ".\n")

    add_entities(query_es("facts", "reddit-*", span, es), "funfact")
    add_entities(query_es("article", "washpost_article*", span, es), "article")
    f.close()
