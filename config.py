from dbs import MusicDB, GameDB, TMDB

dbs = {"music": MusicDB, "games": GameDB, "movies": TMDB}
host = 'search-elastic-crawled-data-ftz4qk7ud65hcmugp2mmylgk4u.us-east-1.es.amazonaws.com'
rdf_name = "articles"
ent_name = "ent_test2"

db = "/home/matulma4/docker/data/labels/fb_db.sqlite"
lookup_url = 'http://34.196.128.143:5000/search/'
