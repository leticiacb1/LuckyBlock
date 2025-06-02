import pytest
import brownie
from brownie import chain, reverts

def test_onwer_clain_balance(lottery, accounts):
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
    lottery.finish_claim_time({"from": user})

    # Not over
    lottery.finish_claim_time({"from": owner})

    claim_duration = lottery.lottery()[18]  # claim_time_duration
    chain.sleep(claim_duration + 1)
    chain.mine()

    tz = lottery.finish_claim_time({"from": owner})
    tz.wait(1)

    assert lottery.lottery()[19] == True

    # --- Owner Claim Balance ---
    initial_balance = owner.balance()
    claim_tx = lottery.claim_balance({"from": owner})
    claim_tx.wait(1)
    final_balance = owner.balance()
    chain.mine()
    assert final_balance > initial_balance, "Owner's balance did not increase after claiming"



