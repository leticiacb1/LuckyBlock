import pytest
import brownie
from brownie import chain, reverts
from web3.exceptions import ContractLogicError

def test_finish_claim_time(lottery, accounts):
    owner = lottery.lottery()[1]
    user = accounts[1]

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
    # Not contract owner
    with pytest.raises((ValueError, ContractLogicError)) as exc_info:
        lottery.finish_claim_time({"from": user})
    assert "Only contract owner can call this" in str(exc_info.value)

    # Not over
    with pytest.raises(ValueError) as exc_info:
        lottery.finish_claim_time({"from": owner})
    assert "Claim time is not over" in str(exc_info.value)

    claim_duration = lottery.lottery()[18]  # claim_time_duration
    chain.sleep(claim_duration + 1)
    chain.mine()

    tz = lottery.finish_claim_time({"from": owner})
    tz.wait(1)

    assert lottery.lottery()[19] == True
