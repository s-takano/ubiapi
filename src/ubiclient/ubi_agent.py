from abc import ABC, abstractmethod
from .schemas import CheckoutBase, Checkout, Account, CheckoutCreate, CheckoutPartialUpdate
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from dateutil import parser
import requests
import os
from .utilities.utils import get_logger

logger = get_logger(__name__)


class SearchCriteria(BaseModel):
    @staticmethod
    def get_default():
        return SearchCriteria(since=datetime(1900, 1, 1))

    def meets(self, checkout : CheckoutBase):
        # set ignoretz=True to ignore timezone so that it's compatible to default datetime
        v_updated_at = checkout["updated_at"]
        updated_at = parser.parse(v_updated_at, ignoretz=True) if isinstance(v_updated_at, str) else v_updated_at
        return updated_at >= self.since

    def to_query_string(self) -> dict:
        # item | since ≤ item.updated_at ⋀ item.updated_at < until ⋀ glb < item.id
        if self.since is None and self.until is None and self.limit is None and self.glb is None:
            return dict()
        query_string = dict()
        if self.since is not None:
            query_string["since"] = self.format_datetime(self.since)
        if self.until is not None:
            query_string["until"] = self.format_datetime(self.until)
        if self.limit is not None:
            query_string["limit"] = str(self.limit)
        if self.glb is not None:
            query_string["glb"] = str(self.glb)
        return query_string

    def format_datetime(self, dt):
        return dt.isoformat(timespec="seconds") + "Z"

    since : Optional[datetime]
    until : Optional[datetime]
    limit : Optional[int]
    glb : Optional[int]

class UbiResponse(BaseModel):
    timestamp : datetime # "2022-06-20T08:32:52Z"

class SimpleReponse(UbiResponse):
    account : Optional[Account]
    checkout : Optional[Checkout]

class CollectionReponse(UbiResponse):
    next_batch_since : datetime # "2022-06-19T21:34:21Z"
    last_updated_at  : datetime # "2022-06-19T21:34:20Z"
    next_url : Optional[str] #": null,

    checkouts : Optional[List[Checkout]]

    class Config:
        alias_generator = lambda str : "next-url" if str=="next_url" else str


class UbiAgentBase(ABC):
    @abstractmethod
    def add(self, resource) -> SimpleReponse:
        ...

    @abstractmethod
    def search(self, resource_uri, criteria) -> CollectionReponse:
        ...

    @abstractmethod
    def get(self, resource_uri) -> SimpleReponse:
        ...

    @abstractmethod
    def update(self, resource_uri, resource) -> None:
        ...

    @abstractmethod
    def delete(self, id) -> None:
        ...


class UbiAgentException(Exception):
    ...

class UbiAgent(UbiAgentBase):
    def __init__(self) -> None:
        super().__init__()
        self.base_uri = "https://ubiregi.com/api/3/"
        self.auth_token = os.environ["X-Ubiregi-Auth-Token"]

    def build_uri(self, resource_uri):
        return self.base_uri + resource_uri

    def http_get(self, resource_uri, headers: dict = None, query_strings : dict = None) -> requests.Response:
        headers_to_get = {
            "Content-Type":"application/json",
            "X-Ubiregi-Auth-Token": self.auth_token
        }
        if headers != None:
            for key in headers:
                headers_to_get[key] = headers[key]

        uri = self.build_uri(resource_uri)
        
        logger.info("http_get:{} {} {}".format(uri, headers_to_get, query_strings))

        return requests.get(uri, headers=headers_to_get, params=query_strings)


    def add(self, resource) -> SimpleReponse:
        ...

    def search(self, resource_uri, criteria : SearchCriteria = None) -> CollectionReponse:
        response = self.http_get(resource_uri, query_strings=criteria.to_query_string() if criteria is not None else None)
        response.raise_for_status()
        return CollectionReponse.parse_obj(response.json())


    def get(self, resource_uri) -> SimpleReponse:
        response = self.http_get(resource_uri)
        response.raise_for_status()
        return SimpleReponse.parse_obj(response.json())


    def update(self, resource_uri, resource) -> None:
        ...

    def delete(self, id) -> None:
        ...



class UbiClientForTest(UbiAgentBase):
    def __init__(self, resp_checkouts : dict) -> None:
        self._resp_checkouts = resp_checkouts
        self.window = 1000
        self.current_pos = 0

    def add(self, resource) -> SimpleReponse:
        idx = max([p["id"] for p in self._resp_checkouts["checkouts"]]) + 1
        resource["id"] = idx
        self._resp_checkouts["checkouts"].append(resource)
        return SimpleReponse(timestamp="2022-06-20T08:32:52Z", checkout=resource)

    def search(self, resource_uri, criteria : SearchCriteria) -> CollectionReponse:
        copy = self._resp_checkouts.copy()

        new_var = [e for e in copy["checkouts"] if criteria.meets(e) ]
        copy["checkouts"] = new_var[self.current_pos : self.current_pos+self.window]
        self.current_pos += self.window

        if len(new_var) <= self.current_pos:
            copy["next-url"] = None
        else:
            copy["next-url"] = "http://nexturi.com"

        return CollectionReponse.parse_obj(copy)

    def get(self, id) -> SimpleReponse:
        return SimpleReponse(timestamp="2022-06-20T08:32:52Z", checkout=next(iter([p for p in self._resp_checkouts["checkouts"] if p["id"] == id]), None))

    def update(self, id: int, resource) -> None:
        for idx, p in enumerate(self._resp_checkouts["checkouts"]):
            if p.id == id:
                db_checkout = self._resp_checkouts["checkouts"][idx]
                update_data = resource.dict(exclude_unset=True)
                updated_checkout = db_checkout.copy(update=update_data)
                self._resp_checkouts["checkouts"][idx] = updated_checkout
                return updated_checkout
        return None

    def delete(self, id) -> None:
        for p in self._resp_checkouts:
            if p.id == id:
                checkout_del = p
                break
        
        if checkout_del:
            self._resp_checkouts.remove(checkout_del)
