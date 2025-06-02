import pytest
import brownie
from brownie import chain, reverts
from web3.exceptions import ContractLogicError

def test_owner_clain_balance(lottery, accounts):
    owner = lottery.lottery()[1]
    user = accounts[1]

    # --- Buy ticket ---
    lottery.buy_ticket(1, [1,2,3,4,5,6], {"from": user, "value": 5})
    lottery.buy_ticket(1, [1,2,3,4,5,6], {"from": user, "value": 5})

    # --- End Betting Phase ---
    chain.sleep(lottery.lottery()[6] - chain.time() + 1)
    chain.mine()
    lottery.finish_bet_time({"from": owner})

    # --- Draw ---
    lottery.draw_happened([0,0,0,0,0,0], {"from": owner})

    # --- End Validation Phase ---
    validation_duration = lottery.lottery()[14]  # validation_time_duration
    chain.sleep(validation_duration + 1)
    chain.mine()

    lottery.finish_validation_time({"from": owner})

    # --- End Claim Phase ---
    claim_duration = lottery.lottery()[18]  # claim_time_duration
    chain.sleep(claim_duration + 1)
    chain.mine()

    tz = lottery.finish_claim_time({"from": owner})
    tz.wait(1)

    assert lottery.lottery()[19] == True

    # --- Owner Claim Balance ---

    # Not contract owner
    with pytest.raises((ValueError,ContractLogicError)) as exc_info:
        lottery.claim_contract_balance({"from": user})
    assert "Only contract owner can call this" in str(exc_info.value)

    # Contract owner
    tx = lottery.claim_contract_balance({"from": owner})
    assert "PrizeClaimed" in tx.events
    assert tx.events["PrizeClaimed"]["user"] == owner
    assert tx.events["PrizeClaimed"]["amount"] == 10



