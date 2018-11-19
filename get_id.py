import sys
import json
#print(sys.argv[1])
ob = json.loads(sys.argv[1])
print(ob["payload"]["loadId"])

