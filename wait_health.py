import http.client, json, time
for i in range(8):
    try:
        c = http.client.HTTPConnection("127.0.0.1", 1102, timeout=3)
        c.request("GET", "/api/health/")
        r = c.getresponse()
        d = json.loads(r.read())
        db = d["data"]["checks"]["database"]
        ca = d["data"]["checks"]["cache"]
        print(f"Try {i+1}: DB={db} Cache={ca}")
        if r.status < 500:
            break
    except Exception as e:
        print(f"Try {i+1}: {e}")
    time.sleep(3)
