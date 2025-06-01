import pytest

def test_lottery_constants(lottery , constants):
    assert lottery.lottery()[0] == constants["lottery_id"]
    assert lottery.lottery()[1] == constants["owner"]
    assert lottery.lottery()[4] == constants["winner_percentage"]
    assert lottery.lottery()[14] == constants["validation_time_duration"]
    assert lottery.lottery()[18] == constants["claim_time_duration"]
    # bet_time_duration not save in a Lottery arg -> bet_end_time = _bet_time_duration + block.timestamp
