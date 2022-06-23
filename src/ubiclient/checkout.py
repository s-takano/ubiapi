from abc import ABC, abstractmethod
from asyncio.log import logger
from datetime import datetime
from dateutil import parser
from typing import Optional, List

from pydantic import BaseModel

from src.ubiclient.utilities.utils import get_logger
from src.ubiclient.schemas import CheckoutBase, Checkout, Account, CheckoutCreate, CheckoutPartialUpdate
import requests

logger = get_logger(__name__)

class CheckoutManagerBase(ABC):
    @abstractmethod
    def add(self, checkout: CheckoutCreate) -> Checkout:
        """
        Adds a checkout to the database
        Args:
            checkout (CheckoutCreate): Checkout to be added

        Returns:
            Checkout: Inserted checkout
        """
        ...

    @abstractmethod
    def search(self) -> Optional[List[Checkout]]:
        """
        Returns checkouts under some criteria
        Returns:
            Optional[List[Checkout]]: List of checkouts
        """
        ...

    @abstractmethod
    def get(self, id: int) -> Optional[Checkout]:
        """
        Returns a checkout from the database
        Args:
            id (int): Checkout ID of the checkout to be updated
        Returns:
            Optional[Checkout]: Checkout
        """
        ...

    @abstractmethod
    def update(self, id: int, checkout: CheckoutPartialUpdate) -> Checkout:
        """
        Updates a checkout
        Args:
            id (int): Checkout ID of the checkout to be updated
            checkout (Checkout): Checkout to update

        Returns:
            Checkout: Updated checkout
        """
        ...

    @abstractmethod
    def delete(self, id: int) -> None:
        """
        Deletes a checkout by id
        Args:
            id (int): Id of the to be deleted checkout
        """
        ...

class SearchCriteria(BaseModel):
    @staticmethod
    def get_default():
        return SearchCriteria(since=datetime(1900, 1, 1))

    def meets(self, checkout : CheckoutBase):
        return parser.parse(checkout["sales_date"]) >= self.since

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


class UbiClientBase(ABC):
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


class UbiClientException(Exception):
    ...

class UbiClient(UbiClientBase):
    def __init__(self, auth_token) -> None:
        super().__init__()
        self.base_uri = "https://ubiregi.com/api/3/"
        self.auth_token = auth_token

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



class UbiClientForTest(UbiClientBase):
    def __init__(self, resp_checkouts : dict) -> None:
        self._resp_checkouts = resp_checkouts

    def add(self, resource) -> SimpleReponse:
        idx = max([p["id"] for p in self._resp_checkouts["checkouts"]]) + 1
        resource["id"] = idx
        self._resp_checkouts["checkouts"].append(resource)
        return SimpleReponse(timestamp="2022-06-20T08:32:52Z", checkout=resource)

    def search(self, resource_uri, criteria) -> CollectionReponse:
        copy = self._resp_checkouts.copy()
        copy["checkouts"] = [e for e in copy["checkouts"] if criteria.meets(e) ]
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


class CheckoutManager(CheckoutManagerBase):

    def __init__(self, client : UbiClientBase) -> None:
        super().__init__()
        self.client = client

    def add(self, checkout: CheckoutCreate) -> Checkout:
        resp = self.client.add(checkout.dict())
        return resp.checkout


    def search(self, criteria : Optional[SearchCriteria] = None) -> Optional[List[Checkout]]:
        if criteria is None:
            criteria = SearchCriteria.get_default()

        resp = self.client.search("accounts/current/checkouts/", criteria)

        return resp.checkouts


    def get(self, id: int) -> Optional[Checkout]:
        resp = self.client.get(id)
        return Checkout.parse_obj(resp.checkout)


    def update(self, id: int, checkout: CheckoutPartialUpdate) -> Checkout:
        resp = self.client.update(id, checkout.dict())
        return resp
    
    def delete(self, id: int) -> None:
        self.client.delete(id)

