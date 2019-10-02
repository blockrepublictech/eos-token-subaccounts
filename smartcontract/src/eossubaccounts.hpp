/**
 *  @file
 *  @copyright Block Republic
 */
 #include <string>

 #include <eosio/eosio.hpp>
 #include <eosio/asset.hpp>

 #define EOS_SYMBOL symbol("EOS", 4)

#include <boost/container/flat_map.hpp>
#include <cmath>

namespace eosio {
  class [[eosio::contract("eossubaccount")]] SubAccounts : public eosio::contract {

  using contract::contract;

  const symbol token_symbol; // The symbol for the currency we play for

  public:
    SubAccounts(name receiver, name code, datastream<const char *> ds) : contract(receiver, code, ds),token_symbol("SYS", 4){}

    // From https://eosio.stackexchange.com/a/4610
    [[eosio::on_notify("*::transfer")]] void ontransfer(eosio::name from, eosio::name to, eosio::asset quantity, std::string memo);
    [[eosio::on_notify("eosio.token::transfer")]] void dummytansfer(eosio::name from, eosio::name to, eosio::asset quantity, std::string memo){ontransfer(from,to,quantity,memo);} // This is a hack, otherwise the ontransfer function won't work

    // https://eosio.stackexchange.com/questions/4381/why-is-eosioon-notifyeosio-tokentransfer-not-working
    using transfer_action = eosio::action_wrapper<eosio::name("transfer"), &SubAccounts::ontransfer>;

    [[eosio::action]]
    void withdraw( name  from, asset amount, std::string memo);
    // Withdraw from the subscription service

    [[eosio::action]]
    void openaccount(name  user, name payer);
    // User opens account on this contract.
    // user = the user who owns the account
    // payer = whomever is paying for the user's RAM

    [[eosio::action]]
    void closeacc(name  user);
    // CLose user account if balance is zero and free any outstanding RAM
    // user = the user who owns the account

  public:
    struct [[eosio::table]] balance {
      asset         funds;

      auto primary_key() const { return funds.symbol.raw(); };
    };

    using balance_table = eosio::multi_index<"balance"_n, balance>;;


  };
}
