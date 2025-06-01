import pytest
import brownie
from brownie import chain, reverts

def test_validate(lottery, accounts):
    owner = lottery.lottery()[1]
    user1 = accounts[1]
    user2 = accounts[2]

    winner_numbers = [1, 2, 3, 4, 5, 6]

    ticket_id = 1

    numbers_1 = [1, 2, 3, 4, 5, 6]
    numbers_2 = [11, 12, 13, 14, 15, 16]
    numbers_3 = [1, 2, 3, 4, 5, 7]

    # --- Buy ticket ---
    lottery.buy_ticket(ticket_id, numbers_1, {"from": user1, "value": 5})
    lottery.buy_ticket(ticket_id, numbers_2, {"from": user1, "value": 5})
    lottery.buy_ticket(ticket_id, numbers_3, {"from": user2, "value": 5})

    # --- End Betting Phase ---
    chain.sleep(lottery.lottery()[6] - chain.time() + 1)
    chain.mine()
    tx = lottery.finish_bet_time({"from": owner})

    # --- Draw ---
    ty = lottery.draw_happened(winner_numbers, {"from": owner})
    ty.wait(1)

    # --- Validation  ---
    lottery.validate({"from": user1})
    lottery.validate({"from": user2})

    # --- Assertions ---
    assert lottery.lottery()[10][0] == user1.address         # Winner address
    assert lottery.lottery()[11]    == 1                     # n_winners == 1
    
    # user2 is not winner
    assert all(lottery.lottery()[10][i] != user2.address for i in range(lottery.lottery()[11]))