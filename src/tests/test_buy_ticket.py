import pytest
from brownie import Lottery, reverts, accounts, web3, chain
from web3.exceptions import ContractLogicError

def test_buy_ticket(lottery, short_lottery, max_number_tickets_lottery):
    user = accounts[1]
    correct_ticket_id = 1
    wrong_ticket_id = 2

    correct_ticket_price = 5
    wrong_ticket_price = 1

    correct_chosen_numbers = [1, 2, 3, 4, 5, 6]
    wrong_size_chosen_numbers = [1, 2, 3, 4, 5]
    wrong_value_chosen_numbers = [1, 2, 3, 4, 5, 61]

    # --- self.bet_in_progress() ---

    # Bet not in progress
    chain.sleep(1)
    chain.mine()
    with pytest.raises(ValueError) as exc_info:
        short_lottery.buy_ticket(correct_ticket_id, correct_chosen_numbers, {"from": user, "value": correct_ticket_price})
    assert "Betting time is over" in str(exc_info.value)

    # --- self.validate_ticket(ticket_id) ---

    # Ticket not a valid Id
    with pytest.raises(ValueError) as exc_info:
        lottery.buy_ticket(wrong_ticket_id, correct_chosen_numbers, {"from": user, "value": correct_ticket_price})
    assert "Invalid Ticket ID" in str(exc_info.value)

    # ---    self.pay_ticket(ticket_id)   ---

    # Invalid payment
    with pytest.raises(ValueError) as exc_info:
        lottery.buy_ticket(correct_ticket_id, correct_chosen_numbers, {"from": user, "value": wrong_ticket_price})
    assert "Insufficient payment" in str(exc_info.value)

    # --- self.register_ticket(msg.sender, ticket_id, user_chosen_numbers) ---

    # -> self.can_buy(ticket_index)
    for _ in range(10):  #  MAX_TICKETS_PER_USER = 10
        max_number_tickets_lottery.buy_ticket(correct_ticket_id, correct_chosen_numbers, {"from": user, "value": correct_ticket_price})

    with pytest.raises(ValueError) as exc_info:
        max_number_tickets_lottery.buy_ticket(correct_ticket_id, correct_chosen_numbers, {"from": user, "value": correct_ticket_price})
    assert "Max number of tickets reached" in str(exc_info.value)

    # -> self.validate_user_numbers(ticket_id, user_chosen_numbers)

    # Invalid chosen numbers
    with pytest.raises(ValueError) as exc_info:
        lottery.buy_ticket(correct_ticket_id, wrong_value_chosen_numbers, {"from": user, "value": correct_ticket_price})
    assert "Invalid number chosen" in str(exc_info.value)

    # Invalid chosen_numbers size
    with pytest.raises(ValueError) as exc_info:
        lottery.buy_ticket(correct_ticket_id, wrong_size_chosen_numbers, {"from": user, "value": correct_ticket_price})
    assert "Sequence has incorrect length" in str(exc_info.value)

    # Successful
    lottery.buy_ticket(correct_ticket_id, correct_chosen_numbers, {"from": user, "value": correct_ticket_price})

    assert lottery.user_ticket_counter(user) == 1
    assert lottery.lottery()[2] == correct_ticket_price                  # check total_amount_raised

    stored_ticket = lottery.lottery_book(lottery.lottery()[0], user, 0)  # first ticket (idx = 0)
    assert stored_ticket[0] == correct_ticket_id
    assert list(stored_ticket[1]) == correct_chosen_numbers
