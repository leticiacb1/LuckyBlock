import pytest
import brownie
from brownie import chain, reverts
from web3.exceptions import ContractLogicError

def test_finish_bet_time(lottery, accounts):
    owner = lottery.lottery()[1]
    user = accounts[1]

    ticket_id = 1
    chosen_numbers = [1, 2, 3, 4, 5, 6]

    # Buy some ticket
    lottery.buy_ticket(ticket_id, chosen_numbers, {"from": user, "value": 5})

    # --- self.only_owner() ---

    # Not contract owner
    with pytest.raises((ValueError, ContractLogicError)) as exc_info:
        lottery.finish_bet_time({"from": user})
    assert "Only contract owner can call this" in str(exc_info.value)

    # --- self.bet_is_over() ---
    # Bet time is not over
    with pytest.raises(ValueError) as exc_info:
        lottery.finish_bet_time({"from": owner})
    assert "Betting time is not over" in str(exc_info.value)

    # Bet time is over
    chain.sleep(lottery.lottery()[6] - chain.time() + 1)      # lottery.lottery()[6] = bet_end_time
    chain.mine()

    tx = lottery.finish_bet_time({"from": owner})
    tx.info()
    tx.wait(1)

    # --- self.lottery.bet_ended ---
    assert lottery.lottery()[7] == True                       # lottery.lottery()[7] = bet_ended

    # --- self.calculate_prize() ---
    total_raised = lottery.lottery()[2]                       # lottery.lottery()[2] = total_amount_raised
    winner_percentage = lottery.lottery()[4]                  # lottery.lottery()[4] = winner_percentage
    expected_prize = (total_raised * winner_percentage) // 100

    assert lottery.lottery()[3] == expected_prize             # lottery.lottery()[3] = prize
