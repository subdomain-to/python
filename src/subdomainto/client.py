from typing import Any, Dict, List, Optional, Type, TypeVar
import httpx
from .errors import AuthenticationError, BadRequestError, ConflictError, ForbiddenError, NotFoundError, ServerError, SubdomainToError, TransportError
from .models import DomainZone, Health, Hostname, Origin, Page, Project, Usage, WebhookEndpoint, WidgetSession, domain_zone, hostname, project

M = TypeVar("M")
class _Resource:
    def __init__(self, client: "SubdomainTo"): self.client=client
class Projects(_Resource):
    def list(self, limit:int=25, cursor:Optional[str]=None)->Page[Project]:
        body=self.client._request("GET","/projects",params={"limit":limit,"cursor":cursor}); meta=body["meta"]
        return Page([project(x) for x in body["data"]],meta["has_more"],meta.get("next_cursor"))
    def create(self,name:str,slug:str,idempotency_key:str)->Project: return project(self.client._data("POST","/projects",json={"name":name,"slug":slug},idempotency_key=idempotency_key))
class Origins(_Resource):
    def create(self,project_id:str,url:str,is_default:bool,idempotency_key:str)->Origin: return Origin(**self.client._data("POST",f"/projects/{project_id}/origins",json={"url":url,"default":is_default},idempotency_key=idempotency_key))
class DomainZones(_Resource):
    def create(self,project_id:str,domain:str,idempotency_key:str)->DomainZone: return domain_zone(self.client._data("POST",f"/projects/{project_id}/domain-zones",json={"domain":domain},idempotency_key=idempotency_key))
class Hostnames(_Resource):
    def list(self,project_id:str,limit:int=25,cursor:Optional[str]=None)->Page[Hostname]:
        body=self.client._request("GET",f"/projects/{project_id}/hostnames",params={"limit":limit,"cursor":cursor});meta=body["meta"]
        return Page([hostname(x) for x in body["data"]],meta["has_more"],meta.get("next_cursor"))
    def create(self,project_id:str,value:str,idempotency_key:str,zone_id:Optional[str]=None,origin_id:Optional[str]=None)->Hostname:
        payload={"hostname":value};
        if zone_id is not None: payload["zone_id"]=zone_id
        if origin_id is not None: payload["origin_id"]=origin_id
        return hostname(self.client._data("POST",f"/projects/{project_id}/hostnames",json=payload,idempotency_key=idempotency_key))
    def get(self,id:str)->Hostname: return hostname(self.client._data("GET",f"/hostnames/{id}"))
    def delete(self,id:str)->Hostname: return hostname(self.client._data("DELETE",f"/hostnames/{id}"))
class Webhooks(_Resource):
    def create(self,url:str,idempotency_key:str,events:Optional[List[str]]=None)->WebhookEndpoint: return WebhookEndpoint(**self.client._data("POST","/webhook-endpoints",json={"url":url,"events":events or ["*"]},idempotency_key=idempotency_key))
class Widget(_Resource):
    def create_session(self,project_id:str,idempotency_key:str,external_customer_id:Optional[str]=None,allowed_origins:Optional[List[str]]=None)->WidgetSession:
        payload:Dict[str,Any]={"project_id":project_id}
        if external_customer_id is not None: payload["external_customer_id"]=external_customer_id
        if allowed_origins: payload["allowed_origins"]=allowed_origins
        return WidgetSession(**self.client._data("POST","/widget-sessions",json=payload,idempotency_key=idempotency_key))
class UsageResource(_Resource):
    def get(self)->Usage: return Usage(**self.client._data("GET","/usage"))

class SubdomainTo:
    def __init__(self,api_key:str,base_url:str="https://api.subdomain.to/v1",http_client:Optional[httpx.Client]=None):
        if not api_key: raise ValueError("api_key is required")
        self.api_key=api_key; self.base_url=base_url.rstrip("/"); self._http=http_client or httpx.Client()
        self.projects=Projects(self);self.origins=Origins(self);self.domain_zones=DomainZones(self);self.hostnames=Hostnames(self);self.webhooks=Webhooks(self);self.widget=Widget(self);self.usage=UsageResource(self)
    def __enter__(self)->"SubdomainTo": return self
    def __exit__(self,*_:Any)->None: self.close()
    def close(self)->None: self._http.close()
    def health(self)->Health: return Health(**self._request("GET","/health",authenticated=False))
    def _data(self,method:str,path:str,**kwargs:Any)->Dict[str,Any]: return self._request(method,path,**kwargs)["data"]
    def _request(self,method:str,path:str,params:Optional[Dict[str,Any]]=None,json:Optional[Dict[str,Any]]=None,idempotency_key:Optional[str]=None,token:Optional[str]=None,authenticated:bool=True)->Dict[str,Any]:
        if idempotency_key is not None and not 1<=len(idempotency_key)<=128: raise ValueError("Idempotency keys must contain between 1 and 128 characters")
        headers={"Accept":"application/json","User-Agent":"subdomainto-python/1.x"}
        if authenticated: headers["Authorization"]="Bearer "+(token or self.api_key)
        if idempotency_key is not None: headers["Idempotency-Key"]=idempotency_key
        try: response=self._http.request(method,self.base_url+path,params={k:v for k,v in (params or {}).items() if v is not None},json=json,headers=headers)
        except httpx.HTTPError as exc: raise TransportError(f"The subdomain.to request failed: {exc}") from exc
        try: body=response.json()
        except ValueError: body={}
        if response.is_success: return body
        error=body.get("error",{}); status=response.status_code; cls:Type[SubdomainToError]={400:BadRequestError,401:AuthenticationError,403:ForbiddenError,404:NotFoundError,409:ConflictError}.get(status,ServerError if status>=500 else SubdomainToError)
        raise cls(status,error.get("code","http_error"),error.get("message",f"HTTP {status}"),error.get("request_id") or response.headers.get("x-request-id"),response.text)
