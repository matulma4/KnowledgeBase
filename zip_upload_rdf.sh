#!/bin/nash
gzip -c articles.rdf > articles.rdf.gz
aws s3 cp articles.rdf.gz s3://knowledge-base-articles/
