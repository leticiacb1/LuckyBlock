from brownie import accounts, Lottery

def test_can_store_value():
    acct = accounts[0]
    contract = Lottery.deploy({"from": acct})
    contract.set(42, {"from": acct})
    assert contract.storedData() == 42