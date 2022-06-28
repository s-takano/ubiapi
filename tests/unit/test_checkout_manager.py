from datetime import datetime
import unittest
from unittest.mock import patch
from os.path import dirname as d
from os.path import abspath
import sys
sys.path.append( "C:\\Projects\\Ponytail\\ubiclient\\src")
print(sys.path)
from ubiclient.schemas import Checkout
from ubiclient.checkout import CheckoutManager, SearchCriteria, create_client
from ubiclient.ubi_agent import SearchCriteria, UbiClientForTest
import json

class TestCheckoutManager(unittest.TestCase):
    def setUp(self) -> None: 
        self.client = UbiClientForTest(self.get_resp_checkouts())
            
    def test_search_all(self):
        with patch("ubiclient.checkout.create_client", return_value = self.client) as mocked_factory:
            sut = CheckoutManager()
            checkouts = sut.search()

            self.assertEqual(len(checkouts), 26)
            mocked_factory.assert_called()


    def test_search_since(self):
        with patch("ubiclient.checkout.create_client", return_value = self.client) as mocked_factory:
            sut = CheckoutManager()
            checkouts = sut.search(SearchCriteria(since=datetime(2022, 6, 25, 12)))

            self.assertEqual(len(checkouts), 6)
            mocked_factory.assert_called()

    def test_search_next_url(self):
        with patch("ubiclient.checkout.create_client", return_value = self.client) as mocked_factory:
            self.client.window = 1

            sut = CheckoutManager()
            checkouts = sut.search()

            self.assertEqual(len(checkouts), 26)
            mocked_factory.assert_called()


    def test_add(self):
        with patch("ubiclient.checkout.create_client", return_value = self.client) as mocked_factory:
            sut = CheckoutManager()

            checkout = Checkout.parse_obj(self.get_resp_checkouts()["checkouts"][0])
            checkout.guid = "new_guid"

            inserted = sut.add(checkout)

            self.assertEqual("new_guid", inserted.guid)
            self.assertEqual(len(sut.search()), 27)
            mocked_factory.assert_called()

    def get_resp_checkouts(self):
        json_path = "{}\{}".format( d(abspath(__file__)), "resp_checkouts.json")
        with open(json_path, 'r') as json_file:
            json_obj = json.load(json_file)
        return json_obj

    def test_get_nothing(self):
        with patch("ubiclient.checkout.create_client", return_value = self.client) as mocked_factory:
            sut = CheckoutManager()
            checkout = sut.get(0)
            self.assertIsNone(checkout)
            mocked_factory.assert_called()

    def test_get(self):
        with patch("ubiclient.checkout.create_client", return_value = self.client) as mocked_factory:
            sut = CheckoutManager()
            checkout = sut.get(285659955)
            self.assertEqual(checkout.id, 285659955)
            mocked_factory.assert_called()

    def test_update_checkout(self):
        pass

    def test_query_string(self):
        self.assertEqual(dict(), SearchCriteria().to_query_string())
        self.assertEqual({"since" : "2022-06-20T08:32:52Z"}, SearchCriteria(since=datetime.fromisoformat("2022-06-20T08:32:52")).to_query_string())
        self.assertEqual({"until" : "2022-06-20T08:32:53Z"}, SearchCriteria(until=datetime.fromisoformat("2022-06-20T08:32:53")).to_query_string())
        self.assertEqual({"glb" : "1"}, SearchCriteria(glb=1).to_query_string())
        self.assertEqual({"limit" : "1"}, SearchCriteria(limit=1).to_query_string())
        self.assertEqual({"since" : "2022-06-20T08:32:52Z", "until" : "2022-06-20T08:32:53Z", "glb" : "2", "limit" : "1"}, 
            SearchCriteria(
                limit=1, 
                glb=2, 
                since=datetime.fromisoformat("2022-06-20T08:32:52"), 
                until=datetime.fromisoformat("2022-06-20T08:32:53")).to_query_string())
