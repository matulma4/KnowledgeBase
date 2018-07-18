#!/bin/bash
gzip -c $1.rdf > $1.rdf.gz
aws s3 cp $1.rdf.gz s3://knowledge-base-articles/
