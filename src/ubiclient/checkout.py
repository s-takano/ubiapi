from abc import ABC, abstractmethod
from typing_extensions import Self
from venv import create
from typing import Optional, List

from .utilities.utils import get_logger
from .schemas import Checkout, Account, CheckoutCreate, CheckoutPartialUpdate
from .ubi_agent import SearchCriteria, Checkout, UbiAgent

logger = get_logger(__name__)

def create_client():
    return UbiAgent()

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

class CheckoutManager(CheckoutManagerBase):


    def __init__(self) -> None:
        super().__init__()
        self.client = create_client()

    def add(self, checkout: CheckoutCreate) -> Checkout:
        resp = self.client.add(checkout.dict())
        return resp.checkout


    def search(self, criteria : Optional[SearchCriteria] = None) -> Optional[List[Checkout]]:
        if criteria is None:
            criteria = SearchCriteria.get_default()

        uri = "accounts/current/checkouts/"

        checkouts = []
        while True:
            # keep getting and concatinating result sets until a response has next-url
            resp = self.client.search(uri, criteria)
            checkouts += resp.checkouts
            if resp.next_url is None:
                break
            uri = resp.next_url

        return checkouts


    def get(self, id: int) -> Optional[Checkout]:
        resp = self.client.get(id)
        if resp.checkout is None:
            return None
        return Checkout.parse_obj(resp.checkout)


    def update(self, id: int, checkout: CheckoutPartialUpdate) -> Checkout:
        resp = self.client.update(id, checkout.dict())
        return resp
    
    def delete(self, id: int) -> None:
        self.client.delete(id)

