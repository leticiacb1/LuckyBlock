import pytest
import brownie
from brownie import chain, reverts

def test_finish_validation_time(lottery, accounts):
    owner = lottery.lottery()[1]
    user = accounts[1]

    winner_numbers = [1, 2, 3, 4, 5, 6]

    user1 = accounts[1]
    ticket_id = 1
    numbers_1 = [1, 2, 3, 4, 5, 6]

    # --- Buy ticket ---
    lottery.buy_ticket(ticket_id, numbers_1, {"from": user1, "value": 5})

    # Bet time is over
    chain.sleep(lottery.lottery()[6] - chain.time() + 1)      # lottery.lottery()[6] = bet_end_time
    chain.mine()

    tx = lottery.finish_bet_time({"from": owner})
    tx.wait(1)

    # Draw happened
    ty = lottery.draw_happened(winner_numbers, {"from": owner})
    ty.wait(1)

    assert lottery.lottery()[8] == True  # draw_occurred

    # user validate win
    lottery.validate({"from": user1})

    # --- self.validation_is_over() ---

    # Is not over
    with pytest.raises(ValueError) as exc_info:
        lottery.finish_validation_time({"from": owner})
    assert "Validate time is not over" in str(exc_info.value)

    # Is over
    validation_duration = lottery.lottery()[14]  # validation_time_duration
    chain.sleep(validation_duration + 1)
    chain.mine()

    # Not contract owner
    with pytest.raises(ValueError) as exc_info:
        lottery.finish_validation_time({"from": user1})
    assert "Only contract owner can call this" in str(exc_info.value)

    # Contract owner
    tz = lottery.finish_validation_time({"from": owner})
    tz.wait(1)

    assert lottery.lottery()[15] == True                  # validation_ended
    assert lottery.lottery()[17] == tz.timestamp          # claim_start_time
    assert lottery.lottery()[20] == True                  # claim_started

    assert lottery.lottery()[12] == lottery.lottery()[3]  # prize_per_winner == total_prize