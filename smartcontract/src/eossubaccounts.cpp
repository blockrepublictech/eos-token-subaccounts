#include "eossubaccounts.hpp"

namespace eosio {

void SubAccounts::withdraw( name  from, asset quantity, std::string memo )
{
  // Validate the transaction
  require_auth( from );
  check( quantity.is_valid(), "invalid quantity" );
  check( quantity.amount > 0, "cannot withdraw negative and zero quantity" );
  check( memo.size() <= 256, "memo has more than 256 bytes" );

  // Check the user has sufficient funds
  balance_table balances(get_self(), from.value);

  auto bal = balances.find( quantity.symbol.raw() );
  check( bal != balances.end(), "user has no subaccount" );
  check( bal->funds.amount >= quantity.amount, "insufficient funds available");

  // Reduce the users balance
  balances.modify( bal, get_self(), [&]( auto& b ) {
    b.funds -= quantity;
  });

  // Send to the withdrawer
  action{
    permission_level{get_self(), "active"_n},
    "eosio.token"_n,
    "transfer"_n,
    std::make_tuple(get_self(), from, quantity, memo)
  }.send();
  }

  void SubAccounts::ontransfer(name from, name to, asset quantity, std::string memo)
  {
    if (from == get_self())
      // Ignore transfers from this contract
      return;
    balance_table balances(get_self(), from.value);

    // Check the user has an account
    auto bal = balances.find( quantity.symbol.raw() );
    if (bal != balances.end())
      // If they do add the tokens to their sub account balance
      balances.modify(bal, get_self(), [&](auto &row) {
        row.funds += quantity;
      });
    else
    {
      // Refund to the sender - we won't accept this
      action{
        permission_level{get_self(), "active"_n},
        "eosio.token"_n,
        "transfer"_n,
        std::make_tuple(get_self(), from, quantity, std::string("Refund, please create an account first."))
      }.send();
    }
  }

  void SubAccounts::openaccount(name  user, name payer)
  {
    require_auth( payer );
    balance_table balance(get_self(), user.value);
    balance.emplace(payer, [&](auto &row) {
      row.funds.amount = 0;
      row.funds.symbol = token_symbol;
    });
  }

  void SubAccounts::closeacc(name  user)
  {
    require_auth( user );
    balance_table balances(get_self(), user.value);
    auto bal = balances.find( token_symbol.raw() );
    check( bal->funds.amount == 0, "Balance must be zero to close account" );
    balances.erase(bal);
  }
}
