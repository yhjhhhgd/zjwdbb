import json

def dumps(data):
    return json.dumps(data, ensure_ascii=False)

def loads(data):
    return json.loads(data) if data else {}
