# eos-token-subaccounts
A generic smart contract to allow users to store tokens. Intended as a generic base for smart contracts that require internal user account balances

## API

The various methods in this smart contract and what they do

### openaccount

**Parameters**
**user** = the name of the user who owns and controls the account
**payer** = the name of the user paying for the ram.

Open a new account for **user**. Payer pays for the ram, note payer can be the
same as user (a user pays for their own ram). Payer is seperate to allow
someone to pay for a user. Eg a service provider that is using this contract.

### closeacc

**Parameters**
**user** = the name of the user who owns and controls the account

Close an account note only the user who owns it can do this even if it was
paid for by another user.
The balance must be zero for this to work. Contracts which reuse this will
probably need to add additional checking

### withdraw

**Parameters**
**user** = the name of the user who owns and controls the account
**amount** = the amount of tokens to withdraw. We can't end up with a negative balance though
**memo** = memo to attach to the withdraw transaction

### ontransfer

This action listens for transfer to and from this contract in any token contract.
Transfers from this contract are ignored.
Transfers to this contract are added to the users internal account balance
Transfers to this contract for user's without an account are immediately returned to them.

## Unit tests

This contract is tested with EOSFactory.

Install EOSFactory from https://www.eosfactory.io following the standard instructions.
Then run the following from the commandline.

`python3 tests/eos_subaccounts.py`
