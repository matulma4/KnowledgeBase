class Entity:
    def __init__(self, name, e_id):
        self.name = name
        self.e_id = e_id
        self.funfacts = []
        self.articles = []
        self.popularity = 0

    def __repr__(self):
        return self.name

    def add_funfact(self, funfact):
        self.funfacts.append(FunFact(funfact.text, funfact.id))
        self.popularity += 1

    def add_article(self, article):
        self.articles.append(NewsArticle(article.body, article.meta.id, article.headline))
        self.popularity += 1


class FunFact:
    def __init__(self, text, id):
        self.text = text
        self.id = id


class NewsArticle:
    def __init__(self, text, id, headline):
        self.text = text
        self.headline = headline
        self.id = id
