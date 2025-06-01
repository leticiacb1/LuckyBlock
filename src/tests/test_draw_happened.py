import pytest
import brownie
from brownie import chain, reverts

def test_draw_happened(lottery, accounts):
    owner = lottery.lottery()[1]
    user = accounts[1]
    winner_numbers = [1, 2, 3, 4, 5, 6]

    # Bet time is over
    chain.sleep(lottery.lottery()[6] - chain.time() + 1) # lottery.lottery()[6] = bet_end_time
    chain.mine()

    tx = lottery.finish_bet_time({"from": owner})
    tx.wait(1)

    # Draw happened
    # Not contract owner
    with pytest.raises(ValueError) as exc_info:
        lottery.draw_happened(winner_numbers, {"from": user})
    assert "Only contract owner can call this" in str(exc_info.value)

    # Contract owner
    ty = lottery.draw_happened(winner_numbers, {"from": owner})
    ty.wait(1)

    assert lottery.lottery()[8] == True                  # draw_occurred
    assert list(lottery.lottery()[9]) == winner_numbers  # winner_combination
    assert lottery.lottery()[13] == ty.timestamp         # validation_start_time
    assert lottery.lottery()[16] == True                 # validation_started