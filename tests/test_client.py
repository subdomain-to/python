import httpx, pytest
from subdomainto import NotFoundError, SubdomainTo

def test_request_authentication_idempotency_and_typed_response():
    seen=[]
    def handler(request:httpx.Request)->httpx.Response:
        seen.append(request); return httpx.Response(201,json={"data":{"id":"p1","name":"Prod","slug":"prod","default_origin":None}})
    client=SubdomainTo("key","https://example.test/v1",httpx.Client(transport=httpx.MockTransport(handler)))
    project=client.projects.create("Prod","prod","idem-1")
    assert project.id=="p1" and seen[0].headers["authorization"]=="Bearer key" and seen[0].headers["idempotency-key"]=="idem-1"

def test_structured_error_mapping():
    transport=httpx.MockTransport(lambda _:httpx.Response(404,headers={"x-request-id":"req_1"},json={"error":{"code":"not_found","message":"Missing"}}))
    client=SubdomainTo("key",http_client=httpx.Client(transport=transport))
    with pytest.raises(NotFoundError) as caught: client.hostnames.get("missing")
    assert caught.value.status_code==404 and caught.value.request_id=="req_1"

def test_all_twelve_contract_operations():
    project={"id":"p1","name":"Prod","slug":"prod","default_origin":None};origin={"id":"o1","url":"https://origin.test","host":"origin.test","port":443}
    hostname={"id":"h1","hostname":"portal.test","type":"exact","status":"active","dns_status":"valid","certificate_status":"issued","routing_status":"active","dns_records":[],"origin":origin,"error":None,"created_at":"2026-07-15T10:00:00Z"};calls=[]
    def handler(request:httpx.Request)->httpx.Response:
        calls.append((request.method,request.url.path));path=request.url.path
        if path.endswith("/health"): body={"status":"ok","service":"subdomain.to","version":"v1"}
        elif path.endswith("/projects") and request.method=="GET": body={"data":[project],"meta":{"has_more":False,"next_cursor":None}}
        elif path.endswith("/projects"): body={"data":project}
        elif path.endswith("/origins"): body={"data":origin}
        elif path.endswith("/domain-zones"): body={"data":{"id":"z1","base_domain":"customers.test","status":"active","dns_status":"valid","certificate_status":"issued","error":None,"dns_records":[]}}
        elif path.endswith("/hostnames") and request.method=="GET": body={"data":[hostname],"meta":{"has_more":False,"next_cursor":None}}
        elif "/hostnames" in path: body={"data":hostname}
        elif path.endswith("/webhook-endpoints"): body={"data":{"id":"w1","url":"https://hook.test","events":["*"],"active":True,"secret":"secret"}}
        elif path.endswith("/widget-sessions"): body={"data":{"token":"jwt","expires_at":"2026-07-15T10:30:00Z","expires_in":1800}}
        else: body={"data":{"active_hostnames":1,"included_hostnames":5,"bandwidth_gb":0,"included_bandwidth_gb":100}}
        return httpx.Response(200,json=body)
    client=SubdomainTo("key","https://api.test/v1",httpx.Client(transport=httpx.MockTransport(handler)))
    client.health();client.projects.list();client.projects.create("Prod","prod","p");client.origins.create("p1","https://origin.test",True,"o");client.domain_zones.create("p1","customers.test","z");client.hostnames.list("p1");client.hostnames.create("p1","portal.test","h");client.hostnames.get("h1");client.hostnames.delete("h1");client.webhooks.create("https://hook.test","w");client.widget.create_session("p1","s");client.usage.get()
    assert len(calls)==12
