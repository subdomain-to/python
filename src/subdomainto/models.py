from dataclasses import dataclass
from typing import Any, Dict, Generic, List, Optional, TypeVar

@dataclass(frozen=True)
class Health: status: str; service: str; version: str
@dataclass(frozen=True)
class Origin: id: str; url: str; host: str; port: int
@dataclass(frozen=True)
class DnsRecord: type: str; name: str; value: str
@dataclass(frozen=True)
class Project:
    id: str; name: str; slug: str; default_origin: Optional[Origin]
@dataclass(frozen=True)
class DomainZone:
    id: str; base_domain: str; status: str; dns_status: str; certificate_status: str; error: Optional[str]; dns_records: List[DnsRecord]
@dataclass(frozen=True)
class Hostname:
    id: str; hostname: str; type: str; status: str; dns_status: str; certificate_status: str; routing_status: str
    dns_records: List[DnsRecord]; origin: Optional[Origin]; error: Optional[str]; created_at: str
@dataclass(frozen=True)
class WebhookEndpoint: id: str; url: str; events: List[str]; active: bool; secret: str
@dataclass(frozen=True)
class WidgetSession: token: str; expires_at: str; expires_in: int
@dataclass(frozen=True)
class Usage: active_hostnames: int; included_hostnames: int; bandwidth_gb: float; included_bandwidth_gb: int
@dataclass(frozen=True)
class WebhookEvent: id: str; event: str; created_at: str; data: Dict[str, Any]
T = TypeVar("T")
@dataclass(frozen=True)
class Page(Generic[T]): items: List[T]; has_more: bool; next_cursor: Optional[str]

def origin(data: Optional[Dict[str, Any]]) -> Optional[Origin]: return None if data is None else Origin(**data)
def project(data: Dict[str, Any]) -> Project: return Project(data["id"], data["name"], data["slug"], origin(data.get("default_origin")))
def dns_records(data: List[Dict[str, Any]]) -> List[DnsRecord]: return [DnsRecord(**item) for item in data]
def domain_zone(data: Dict[str, Any]) -> DomainZone: return DomainZone(data["id"],data["base_domain"],data["status"],data["dns_status"],data["certificate_status"],data.get("error"),dns_records(data.get("dns_records",[])))
def hostname(data: Dict[str, Any]) -> Hostname: return Hostname(data["id"],data["hostname"],data["type"],data["status"],data["dns_status"],data["certificate_status"],data["routing_status"],dns_records(data.get("dns_records",[])),origin(data.get("origin")),data.get("error"),data.get("created_at",""))
