curl -X POST \
     -H "Content-Type: application/json" \
     -d @./test/route.json \
     -o ./test/route.json.out \
     http://localhost:8002/sources_to_targets