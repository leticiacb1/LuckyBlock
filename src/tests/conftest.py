import pytest
from brownie import Lottery, accounts

@pytest.fixture(scope="module")
def constants():
    return {
        "lottery_id": 1,
        "owner": accounts[0],
        "winner_percentage": 50,
        "bet_time_duration": 90,
        "validation_time_duration": 60,
        "claim_time_duration": 60,
    }

@pytest.fixture(scope="module")
def short_time_constants():
    return {
        "lottery_id": 1,
        "owner": accounts[0],
        "winner_percentage": 50,
        "bet_time_duration": 1,
        "validation_time_duration": 1,
        "claim_time_duration": 1,
    }


@pytest.fixture
def lottery(constants):
    return Lottery.deploy(
        constants["lottery_id"],
        constants["winner_percentage"],
        constants["bet_time_duration"],
        constants["validation_time_duration"],
        constants["claim_time_duration"],
        {'from': constants["owner"]}
    )

@pytest.fixture
def max_number_tickets_lottery(constants):
    return Lottery.deploy(
        constants["lottery_id"],
        constants["winner_percentage"],
        constants["bet_time_duration"],
        constants["validation_time_duration"],
        constants["claim_time_duration"],
        {'from': constants["owner"]}
    )

@pytest.fixture
def short_lottery(short_time_constants):
    return Lottery.deploy(
        short_time_constants["lottery_id"],
        short_time_constants["winner_percentage"],
        short_time_constants["bet_time_duration"],
        short_time_constants["validation_time_duration"],
        short_time_constants["claim_time_duration"],
        {'from': short_time_constants["owner"]}
    )