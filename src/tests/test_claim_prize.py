import pytest
import brownie
from brownie import chain, reverts

def test_claim_prize(lottery, accounts):
    owner = lottery.lottery()[1]
    user1 = accounts[1]
    user2 = accounts[2]
    user3 = accounts[3]

    winner_numbers = [1, 2, 3, 4, 5, 6]

    ticket_id = 1

    numbers_1 = [1, 2, 3, 4, 5, 6]
    numbers_2 = [11, 12, 13, 14, 15, 16]
    numbers_3 = [1, 2, 3, 4, 5, 7]
    numbers_4 = [1, 2, 3, 4, 5, 6]

    # --- Buy ticket ---
    lottery.buy_ticket(ticket_id, numbers_1, {"from": user1, "value": 5})
    lottery.buy_ticket(ticket_id, numbers_2, {"from": user1, "value": 5})
    lottery.buy_ticket(ticket_id, numbers_3, {"from": user2, "value": 5})
    lottery.buy_ticket(ticket_id, numbers_4, {"from": user3, "value": 5})

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
    lottery.validate({"from": user3})

    # --- Assertions ---
    assert lottery.lottery()[10][0] == user1.address         # Winner address
    assert lottery.lottery()[10][1] == user3.address
    assert lottery.lottery()[11]    == 2                     # n_winners == 2

    # --- End Validation Phase ---
    validation_duration = lottery.lottery()[14]              # validation_time_duration
    chain.sleep(validation_duration + 1)
    chain.mine()

    tz = lottery.finish_validation_time({"from": owner})
    tz.wait(1)

    total_prize = lottery.lottery()[3]
    prize_per_winner = total_prize // lottery.lottery()[11]

    assert lottery.lottery()[12] == prize_per_winner         # prize_per_winner

    # --- Claim prize ---

    tw1 = lottery.claim_prize({"from": user1})
    assert "PrizeClaimed" in tw1.events
    assert tw1.events["PrizeClaimed"]["user"] == user1
    assert tw1.events["PrizeClaimed"]["amount"] == prize_per_winner

    tw2 = lottery.claim_prize({"from": user2})
    assert "PrizeClaimed" not in tw2.events

    tw3 = lottery.claim_prize({"from": user3})
    assert "PrizeClaimed" in tw3.events
    assert tw3.events["PrizeClaimed"]["user"] == user3
    assert tw3.events["PrizeClaimed"]["amount"] == prize_per_winner
