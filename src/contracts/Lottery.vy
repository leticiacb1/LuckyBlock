# @version ^0.4.1

storedData: public(uint256)

@external
def set(x: uint256):
    self.storedData = x