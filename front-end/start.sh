
# Start servers and ElasticSearch

echo "Starting ElasticSearch Server"
/Users/ronanmanoj/Documents/elasticsearch-7.5.2/bin/elasticsearch

echo "Starting Kibana Server"
/Users/ronanmanoj/Documents/kibana-7.5.2-darwin-x86_64/bin/kibana

echo "Starting Postgres Test Database"
psql test