import hashlib,hmac,json,pytest
from subdomainto import InvalidWebhookError,verify_webhook
def test_verifies_webhook():
    body=json.dumps({"id":"e1","event":"hostname.created","created_at":"2026-07-15T10:00:00Z","data":{"id":"h1"}},separators=(",",":")).encode();timestamp=1752573600
    signature=hmac.new(b"secret",str(timestamp).encode()+b"."+body,hashlib.sha256).hexdigest()
    assert verify_webhook(body,f"t={timestamp},v1={signature}","secret",now=timestamp).event=="hostname.created"
def test_rejects_stale_webhook():
    with pytest.raises(InvalidWebhookError): verify_webhook(b"{}","t=1,v1=bad","secret",now=1000)
