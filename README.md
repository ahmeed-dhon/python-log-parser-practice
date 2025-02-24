### LOG PARSER AND INGESTION SCRIPT

### Why Elasticsearch + Kibana?
1. Simple to setup
2. Easy to operated
3. Already familiar with its interface and how its run

#### How to run the script
1. Run `docker compose up -d` to start single-node elasticsearch and kibana locally
2. Run `python3 processor.py` to parse and put the processed log to the elasticsearch
