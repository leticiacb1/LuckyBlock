# @version ^0.4.1

# --------------------------------------
# ------------ CONSTANTS ---------------
# --------------------------------------

MAX_TICKETS_PER_USER: constant(uint256) = 10
MAX_NUMBER_OF_WINNERS: constant(uint256) = 100

MIN_VALID_NUMBER: constant(uint256) = 1
MAX_VALID_NUMBER: constant(uint256) = 60

CHOOSEN_NUMBERS_SIZE: constant(uint256) = 6

# --------------------------------------
# ------------ STRUCT ------------------
# --------------------------------------

struct Ticket:
    amount_of_numbers: uint256
    price: uint256

tickets: public(HashMap[uint256, Ticket])
valid_ticket_ids: public(HashMap[uint256, bool])

# Maps users to their purchased tickets
struct UserTicket:
    ticket_id: uint256
    user_chosen_numbers: uint256[CHOOSEN_NUMBERS_SIZE]  # max of choosen numbers

# { user : ticket_counter }
user_ticket_counter: public(HashMap[address, uint256])

# Records all information from a Lottery "round"
struct Lottery:
    id: uint256
    owner: address

    total_amount_raised: uint256

    prize: uint256
    winner_percentage: uint256

    bet_start_time: uint256
    bet_end_time: uint256
    bet_ended: bool

    draw_occurred: bool
    winner_combination: uint256[CHOOSEN_NUMBERS_SIZE]  # 6 winner numbers
    winners_address: address[MAX_NUMBER_OF_WINNERS]    # Max of 1000 winners
    n_winners: uint256
    prize_per_winner: uint256

    validation_start_time: uint256
    validation_time_duration: uint256
    validation_ended: bool
    validation_started: bool

    claim_start_time: uint256
    claim_time_duration: uint256
    claim_ended: bool
    claim_started: bool

lottery: public(Lottery)

# { lottery_id : {
#      user_address : { 
#         ticket_index :  UserTicket(ticket_id, user_chosen_numbers)    
#      }
#   } 
# }
lottery_book: public(HashMap[uint256, HashMap[address, HashMap[uint256, UserTicket]]])

event PrizeClaimed:
    user: address
    amount: uint256

# --------------------------------------
# ------------ DEPLOY ------------------
# --------------------------------------

@deploy
def __init__(
        _id: uint256,
        _winner_percentage: uint256,
        _bet_time_duration: uint256,
        _validation_time_duration: uint256,
        _claim_time_duration: uint256
):
    self.set_ticket()
    self.lottery = Lottery({
        id: _id,

        owner: msg.sender,

        total_amount_raised: 0,
        prize: 0,

        winner_percentage: _winner_percentage,

        bet_start_time: block.timestamp,
        bet_end_time: _bet_time_duration + block.timestamp,
        bet_ended: False,

        draw_occurred: False,
        winner_combination: empty(uint256[CHOOSEN_NUMBERS_SIZE]),
        winners_address: empty(address[MAX_NUMBER_OF_WINNERS]),
        n_winners: 0,
        prize_per_winner: 0,

        validation_start_time: 0,
        validation_time_duration: _validation_time_duration,
        validation_ended: False,
        validation_started: False,

        claim_start_time: 0,
        claim_time_duration: _claim_time_duration,
        claim_ended: False,
        claim_started: False
    })


# -------------------------------------------
# ---------- AUXILIARY FUNCTIONS-------------
# -------------------------------------------

@internal
def set_ticket():
    ticket_id: uint256 = 1
    amount_of_numbers: uint256 = CHOOSEN_NUMBERS_SIZE
    price: uint256 = 5

    ticket: Ticket = Ticket({
        amount_of_numbers: amount_of_numbers,
        price: price
    })

    self.tickets[ticket_id] = ticket
    self.valid_ticket_ids[ticket_id] = True


@internal
def only_owner():
    assert msg.sender == self.lottery.owner, "Only contract owner can call this"


@internal
def bet_in_progress():
    assert self.lottery.bet_end_time > block.timestamp, "Betting time is over"


@internal
def bet_is_over():
    assert self.lottery.bet_end_time < block.timestamp, "Betting time is not over"


@internal
def validation_in_progress():
    assert self.lottery.validation_started
    assert self.lottery.validation_start_time + self.lottery.validation_time_duration > block.timestamp, "Validate time is over"


@internal
def validation_is_over():
    assert self.lottery.validation_started
    assert self.lottery.validation_start_time + self.lottery.validation_time_duration < block.timestamp, "Validate time is not over"


@internal
def claim_in_progress():
    assert self.lottery.claim_started
    assert self.lottery.claim_start_time + self.lottery.claim_time_duration > block.timestamp, "Claim time is over"


@internal
def claim_is_over():
    assert self.lottery.claim_started
    assert self.lottery.claim_start_time + self.lottery.claim_time_duration < block.timestamp, "Claim time is not over"


@internal
def validate_ticket(id: uint256):
    assert self.valid_ticket_ids[id], "Invalid Ticket ID"


@internal
def can_buy(ticket_index: uint256):
    assert MAX_TICKETS_PER_USER >= ticket_index + 1, "Max number of tickets reached"


@internal
@payable
def pay_ticket(id: uint256):
    assert msg.value >= self.tickets[id].price, "Insufficient payment"


@internal
def validate_user_numbers(ticket_id: uint256, user_chosen_numbers: uint256[6]):
    for i: uint256 in range(CHOOSEN_NUMBERS_SIZE):
        if user_chosen_numbers[i] < MIN_VALID_NUMBER or user_chosen_numbers[i] > MAX_VALID_NUMBER:
            assert False, "Invalid number chosen"

@internal
def register_ticket(user: address, ticket_id: uint256, user_chosen_numbers: uint256[6]):
    ticket_index: uint256 = self.user_ticket_counter[user]

    self.can_buy(ticket_index)
    self.validate_user_numbers(ticket_id, user_chosen_numbers)

    self.lottery_book[self.lottery.id][user][ticket_index] = UserTicket({
        ticket_id: ticket_id,
        user_chosen_numbers: user_chosen_numbers
    })

    self.user_ticket_counter[user] = ticket_index + 1
    self.lottery.total_amount_raised += self.tickets[ticket_id].price


@internal
def calculate_prize():
    # winner_percentage % of total_amount_raised (Integer value)
    self.lottery.prize = (self.lottery.total_amount_raised * self.lottery.winner_percentage) // 100


@internal
def same_numbers(user_numbers: uint256[6]) -> bool:
    for i: uint256 in range(CHOOSEN_NUMBERS_SIZE):
        if user_numbers[i] != self.lottery.winner_combination[i]:
            return False
    return True

@internal
def validate_winner(user: address, user_numbers: uint256[6]):
    assert self.lottery.n_winners < MAX_NUMBER_OF_WINNERS
    if self.same_numbers(user_numbers):
        self.lottery.winners_address[self.lottery.n_winners] = user
        self.lottery.n_winners += 1


# ------------------------------------------------
# ------------ ACTION FUNCTIONS ------------------
# ------------------------------------------------

@external
@payable
def buy_ticket(ticket_id: uint256, user_chosen_numbers: uint256[6]):
    self.bet_in_progress()
    self.validate_ticket(ticket_id)
    self.pay_ticket(ticket_id)
    self.register_ticket(msg.sender, ticket_id, user_chosen_numbers)

@external
def finish_bet_time():
    self.only_owner()
    self.bet_is_over()
    self.lottery.bet_ended = True
    self.calculate_prize()

@external
def draw_happened(winner_numbers: uint256[6]):
    self.only_owner()
    assert self.lottery.bet_ended

    self.lottery.draw_occurred = True
    self.lottery.winner_combination = winner_numbers

    self.lottery.validation_start_time = block.timestamp
    self.lottery.validation_started = True

@external
def validate():
    self.validation_in_progress()

    for i: uint256 in range(MAX_TICKETS_PER_USER):
        ticket: UserTicket = self.lottery_book[self.lottery.id][msg.sender][i]
        user_numbers: uint256[6] = ticket.user_chosen_numbers
        self.validate_winner(msg.sender, user_numbers)

@external
def finish_validation_time():
    self.only_owner()
    assert self.lottery.draw_occurred
    self.validation_is_over()
    self.lottery.validation_ended = True

    self.lottery.claim_start_time = block.timestamp
    self.lottery.claim_started = True

    if self.lottery.n_winners > 0:
        self.lottery.prize_per_winner = self.lottery.prize // self.lottery.n_winners

@external
def claim_prize():
    self.claim_in_progress()

    for i: uint256 in range(MAX_NUMBER_OF_WINNERS):
        winner_address: address = self.lottery.winners_address[i]
        if winner_address == msg.sender:
            send(msg.sender, self.lottery.prize_per_winner)
            log PrizeClaimed(msg.sender, self.lottery.prize_per_winner)

@external
def finish_claim_time():
    self.only_owner()
    assert self.lottery.validation_ended
    self.claim_is_over()
    self.lottery.claim_ended = True

@external
def claim_contract_balance():
    self.only_owner()
    assert self.lottery.claim_ended, "Claim time is not over"
    if self.balance > 0:
        send(msg.sender, self.balance)
