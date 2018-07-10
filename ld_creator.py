our_namespace = "http://rdf.article.com/ns/"
fb_namespace = "http://rdf.freebase.com/ns/"
owl_namespace = "http://www.w3.org/2002/07/owl#"


def create_property(text, headline, concept_id, property, object_id):
    subject_1 = "<" + fb_namespace + concept_id + ">"
    predicate_1 = "<" + our_namespace + "in" + property.capitalize() + ">"  # TODO change to existing relation
    object_1 = "<" + our_namespace + property + "/" + object_id + ">"

    subject_2 = "<" + our_namespace + property + "/" + object_id + ">"
    predicate_2 = "<" + our_namespace + "hasText>"  # TODO change to existing relation
    object_2 = "\"" + text + "\"" + "@en"
    spo_3 = None
    if headline is not None:
        subject_3 = "<" + our_namespace + property + "/" + object_id + ">"
        predicate_3 = "<" + our_namespace + "hasHeadline>"  # TODO change to existing relation
        object_3 = "\"" + headline + "\"" + "@en"
        spo_3 = " ".join([subject_3, predicate_3, object_3, "."])

    return " ".join([subject_1, predicate_1, object_1, "."]), " ".join([subject_2, predicate_2, object_2, "."]), spo_3


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


if __name__ == '__main__':
    print(create_property("Hello world", "m.12314", "funfact",""))
