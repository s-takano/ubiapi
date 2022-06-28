print(__name__)

from datetime import datetime
import unittest

from ubiclient.checkout import UbiAgent, SearchCriteria

class TestUbiClient(unittest.TestCase):
    def setUp(self) -> None:
        self.client = UbiAgent()

    def test_add(self):
        self.fail()

    def test_search(self):
        response = self.client.search("accounts/current/checkouts")
        self.assertIsNotNone(response.checkouts)
        self.assertGreater(len(response.checkouts), 0)

    def test_search_since(self):
        response = self.client.search("accounts/current/checkouts",
                                      SearchCriteria(since=datetime(2022, 6, 19, hour=20, minute=56, second=39)))
        print(response.checkouts)
        self.assertGreaterEqual(len(response.checkouts), 2)

    def test_search_until(self):
        response = self.client.search("accounts/current/checkouts",
                                      SearchCriteria(until=datetime(2022, 6, 19, hour=21, minute=30, second=0)))
        print(response.checkouts)
        self.assertEqual(len(response.checkouts), 2)

    def test_search_since_until(self):
        response = self.client.search("accounts/current/checkouts",
                                      SearchCriteria(
                                          since=datetime(2022, 6, 19, hour=20, minute=57, second=0),
                                          until=datetime(2022, 6, 19, hour=21, minute=30, second=0)))
        print(response.checkouts)
        self.assertEqual(len(response.checkouts), 1)

    def test_search_glb(self):
        response = self.client.search("accounts/current/checkouts")
        all_checkouts = response.checkouts
        
        # glb < id
        response = self.client.search("accounts/current/checkouts",
                                      SearchCriteria(glb=all_checkouts[0].id))
        self.assertEqual(len(response.checkouts), len(all_checkouts)-1)


    def test_get(self):
        response = self.client.get("accounts/current")
        self.assertIsNotNone(response.account)
        self.assertTrue(isinstance(response.account.id, int))
        
    def test_update(self):
        pass

    def test_delete(self):
        pass
