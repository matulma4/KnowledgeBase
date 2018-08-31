our_namespace = "http://rdf.article.com/ns/"
fb_namespace = "http://rdf.freebase.com/ns/"
owl_namespace = "http://www.w3.org/2002/07/owl#"
xsd_namespace = "http://www.w3.org/2001/XMLSchema#"


def create_property(concept_id, object_id):
    subject = "<" + fb_namespace + concept_id + ">"
    predicate = "<" + our_namespace + "inArticle>"
    _object = "<" + our_namespace + object_id + ">"

    return " ".join([subject, predicate, _object, "."])


def create_text(object_id, text, prop):
    subject = "<" + our_namespace + object_id + ">"
    predicate = "<" + our_namespace + "has" + prop + ">"
    _object = "\"" + text + "\"" + "@en"
    return " ".join([subject, predicate, _object, "."])


def create_type(prop, object_id):
    subject = "<" + our_namespace + object_id + ">"
    predicate = "<" + our_namespace + "isType>"
    _object = "<" + our_namespace + prop + ">"
    return " ".join([subject, predicate, _object, "."])


def create_date(prop, object_id):
    subject = "<" + our_namespace + object_id + ">"
    predicate = "<" + our_namespace + "hasDate>"
    _object = "\"" + prop + "\"" + "^^<" + xsd_namespace + "date>"
    return " ".join([subject, predicate, _object, "."])


def create_topic(prop, object_id):
    subject = "<" + our_namespace + object_id + ">"
    predicate = "<" + our_namespace + "isTopic>"
    _object = "<" + our_namespace + "topics/" + prop + ">"
    return " ".join([subject, predicate, _object, "."])


def create_entity(ent_name):
    k_name = ent_name.name.lower().replace(" ", "_")
    for c in "\'.,/":
        k_name = k_name.replace(c, "")
    k_name = "entity/" + k_name
    subject = "<" + our_namespace + k_name + ">"
    predicate = "<http://www.w3.org/2000/01/rdf-schema#label>"
    _object = "\"" + ent_name.name + "\"" + "@en"

    # sameas = subject + " <" + owl_namespace + "sameAs> " +

    return " ".join([subject, predicate, _object, "."]), k_name

