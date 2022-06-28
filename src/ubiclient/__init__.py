if __name__ != "src.ubiclient": # don't import in Test
    from ubiclient.schemas import Checkout, CheckoutBase, CheckoutCreate, CheckoutPartialUpdate
    from ubiclient.checkout import CheckoutManager, CheckoutManagerBase
