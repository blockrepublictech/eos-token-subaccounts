'''An example of functional test.

Note that the declarations
    `
    MASTER = MasterAccount()
    HOST = Account()
    ALICE = Account()
    BOB = Account()
    CAROL = Account()
    `
are abundant: they are in place to satisfy the linter, whu complains about
dynamically created objects.
'''
import unittest
from eosfactory.eosf import *

verbosity([Verbosity.INFO, Verbosity.OUT, Verbosity.TRACE, Verbosity.DEBUG])

CONTRACT_WORKSPACE = "_GxeBtrni4AqyEgptLzyjtYngNBstDXgY"

# Actors of the test:
MASTER = MasterAccount()
HOST = Account()
ALICE = Account()
CAROL = Account()
BOB = Account()

class Test(unittest.TestCase):

    def run(self, result=None):
        super().run(result)

    @classmethod
    def setUpClass(cls):
        SCENARIO('''
        Create a contract from template, then build and deploy it.
        ''')
        reset()
        create_master_account("MASTER")

        COMMENT('''
        Create test accounts:
        ''')
        create_account("ALICE", MASTER)
        create_account("CAROL", MASTER)
        create_account("BOB", MASTER)

    def initialise_eosio_token(self):
        # Copied from eosfactories' eosio.token tests set up some useful account balances
        COMMENT('''
        Create, build and deploy the eosio token contract:
        ''')
        create_account("HOST_EOSIO_TOKEN", MASTER, account_name="eosio.token")
        HOST_EOSIO_TOKEN.info()
        eosio_token = Contract(HOST_EOSIO_TOKEN, project_from_template(
            CONTRACT_WORKSPACE, template="eosio_token", remove_existing=True))
        eosio_token.build()
        eosio_token.deploy()

        COMMENT('''
        Initialize the token and send some tokens to one of the accounts:
        ''')
        HOST_EOSIO_TOKEN.push_action(
            "create",
            {
                "issuer": MASTER,
                "maximum_supply": "1000000000.0000 SYS",
                "can_freeze": "0",
                "can_recall": "0",
                "can_whitelist": "0"
            },
            force_unique=True,
            permission=[(MASTER, Permission.ACTIVE), (HOST_EOSIO_TOKEN, Permission.ACTIVE)])
        print("'trace[\"console\"]' sum is '{}'".format(HOST_EOSIO_TOKEN.action.console))
        logger.DEBUG(HOST_EOSIO_TOKEN.action.act)

        HOST_EOSIO_TOKEN.push_action(
            "issue",
            {
                "to": ALICE, "quantity": "100.0000 SYS", "memo": ""
            },
            force_unique=True,
            permission=(MASTER, Permission.ACTIVE))
        print("'trace[\"console\"]' sum is '{}'".format(HOST_EOSIO_TOKEN.action.console))
        logger.DEBUG(HOST_EOSIO_TOKEN.action.act)

        COMMENT('''
        Execute a series of transfers between the accounts:
        ''')

        HOST_EOSIO_TOKEN.push_action(
            "transfer",
            {
                "from": ALICE, "to": CAROL,
                "quantity": "25.0000 SYS", "memo":""
            },
            force_unique=True,
            permission=(ALICE, Permission.ACTIVE))
        logger.DEBUG(HOST_EOSIO_TOKEN.action.act)

        HOST_EOSIO_TOKEN.push_action(
            "transfer",
            {
                "from": CAROL, "to": BOB,
                "quantity": "11.0000 SYS", "memo": ""
            },
            permission=(CAROL, Permission.ACTIVE))
        logger.DEBUG(HOST_EOSIO_TOKEN.action.act)

        HOST_EOSIO_TOKEN.push_action(
            "transfer",
            {
                "from": CAROL, "to": BOB,
                "quantity": "2.0000 SYS", "memo": ""
            },
            force_unique=True,
            permission=(CAROL, Permission.ACTIVE))
        logger.DEBUG(HOST_EOSIO_TOKEN.action.act)

        HOST_EOSIO_TOKEN.push_action(
            "transfer",
            {
                "from": BOB, "to": ALICE, \
                "quantity": "2.0000 SYS", "memo":""
            },
            force_unique=True,
            permission=(BOB, Permission.ACTIVE))
        logger.DEBUG(HOST_EOSIO_TOKEN.action.act)

        COMMENT('''
        Verify the outcome:
        ''')

        table_ALICE = HOST_EOSIO_TOKEN.table("accounts", ALICE)
        table_BOB = HOST_EOSIO_TOKEN.table("accounts", BOB)
        table_CAROL = HOST_EOSIO_TOKEN.table("accounts", CAROL)

        self.assertEqual(
            table_ALICE.json["rows"][0]["balance"], '77.0000 SYS',
            '''assertEqual(table_ALICE.json["rows"][0]["balance"], '77.0000 SYS')''')
        self.assertEqual(
            table_BOB.json["rows"][0]["balance"], '11.0000 SYS',
            '''assertEqual(table_BOB.json["rows"][0]["balance"], '11.0000 SYS')''')
        self.assertEqual(
            table_CAROL.json["rows"][0]["balance"], '12.0000 SYS',
            '''assertEqual(table_CAROL.json["rows"][0]["balance"], '12.0000 SYS')''')

    def initialise_eossubaccounts(self):
        COMMENT('''
        Create, build and deploy the EOS Sub Account contract:
        ''')
        create_account("HOST_EOS_SUBACCOUNTS", MASTER, account_name="eoschess")
        HOST_EOS_SUBACCOUNTS.set_account_permission(add_code=True)
        HOST_EOS_SUBACCOUNTS.info()
        COMMENT("EOS Chess Info")
        smart = Contract(HOST_EOS_SUBACCOUNTS, '/home/mark/eoschess-smartcontract/smartcontract/')
        smart.build()
        smart.deploy()

    def test_functional(self):
        self.initialise_eosio_token()

        self.initialise_eossubaccounts()

        COMMENT('''
        Test Alice has no account:
        ''')
        table_ALICE = HOST_EOS_SUBACCOUNTS.table("balance", ALICE)
        self.assertEqual(
            len(table_ALICE.json["rows"]), 0,
            "Account balance exists")

        COMMENT('''
        Test Alice can initialise an account. We need this because Alice must pay for the RAM herself
        ''')
        HOST_EOS_SUBACCOUNTS.push_action(
            "openaccount", {"user":ALICE, "payer":ALICE},
            permission=(ALICE, Permission.ACTIVE),
            force_unique=True)
        table_ALICE = HOST_EOS_SUBACCOUNTS.table("balance", ALICE)
        self.assertEqual(
            table_ALICE.json["rows"][0]["funds"], '0.0000 SYS',
            "Account balance is not zero")


        COMMENT('''
        Test an action for CAROL, including the debug buffer:
        ''')

        COMMENT('''
        WARNING: This action should fail due to authority mismatch!
        ''')
        with self.assertRaises(MissingRequiredAuthorityError):
            # Carol attempts to make Alice pay for her RAM
            HOST_EOS_SUBACCOUNTS.push_action(
                "openaccount", {"user":CAROL, "payer":ALICE},
                permission=(CAROL, Permission.ACTIVE))


        COMMENT('''
        Check the before balance:
        ''')

        table_ALICE = HOST_EOSIO_TOKEN.table("accounts", ALICE)
        table_EOSCHESS = HOST_EOSIO_TOKEN.table("accounts", HOST_EOS_SUBACCOUNTS)
        table_CAROL = HOST_EOSIO_TOKEN.table("accounts", CAROL)

        self.assertEqual(
            table_ALICE.json["rows"][0]["balance"], '77.0000 SYS',
            '''assertEqual(table_ALICE.json["rows"][0]["balance"], '77.0000 SYS')''')
        self.assertEqual(
            len(table_EOSCHESS.json["rows"]), 0,
            "EOSCHESS balance not zero")
        self.assertEqual(
            table_CAROL.json["rows"][0]["balance"], '12.0000 SYS',
            '''assertEqual(table_CAROL.json["rows"][0]["balance"], '12.0000 SYS')''')

        COMMENT('''
        Try a token transfer with EOSChess listening
        ''')
        HOST_EOSIO_TOKEN.push_action(
            "transfer",
            {
                "from": ALICE, "to": HOST_EOS_SUBACCOUNTS,
                "quantity": "1.0000 SYS", "memo":""
            },
            force_unique=True,
            permission=(ALICE, Permission.ACTIVE))
        logger.DEBUG(HOST_EOSIO_TOKEN.action.act)
        table_ALICE = HOST_EOS_SUBACCOUNTS.table("balance", ALICE)
        self.assertEqual(
            table_ALICE.json["rows"][0]["funds"], '1.0000 SYS',
            "Account balance incorrect")

        COMMENT('''
        Check the after balance:
        ''')
        table_ALICE = HOST_EOSIO_TOKEN.table("accounts", ALICE)
        table_EOSCHESS = HOST_EOSIO_TOKEN.table("accounts", HOST_EOS_SUBACCOUNTS)

        self.assertEqual(
            table_ALICE.json["rows"][0]["balance"], '76.0000 SYS',
            '''assertEqual(table_ALICE.json["rows"][0]["balance"], '77.0000 SYS')''')
        self.assertEqual(
            table_EOSCHESS.json["rows"][0]["balance"], '1.0000 SYS',
            '''assertEqual(table_ALICE.json["rows"][0]["balance"], '77.0000 SYS')''')

        COMMENT('''
        Try an invalid token transfer from Carol (who does not have an account)
        ''')
        HOST_EOSIO_TOKEN.push_action(
            "transfer",
            {
                "from": CAROL, "to": HOST_EOS_SUBACCOUNTS,
                "quantity": "1.0000 SYS", "memo":""
            },
            force_unique=True,
            permission=(CAROL, Permission.ACTIVE))
        logger.DEBUG(HOST_EOSIO_TOKEN.action.act)
        table_CAROL = HOST_EOS_SUBACCOUNTS.table("balance", CAROL)
        """self.assertEqual(
            table_CAROL.json["rows"][0]["funds"], '0.0000 SYS',
            "Account balance incorrect")"""
        try:
            table_CAROL = HOST_EOS_SUBACCOUNTS.table("balance", CAROL)
        except Error as ex:
            self.assertTrue(str(ex.message).find("Error 3060003: Contract Table Query Exception") >= 0)

        COMMENT('''
        Check the after balance it should not have changed:
        ''')
        table_CAROL = HOST_EOSIO_TOKEN.table("accounts", CAROL)
        table_EOSCHESS = HOST_EOSIO_TOKEN.table("accounts", HOST_EOS_SUBACCOUNTS)

        self.assertEqual(
            table_CAROL.json["rows"][0]["balance"], '12.0000 SYS',
            '''assertEqual(table_CAROL.json["rows"][0]["balance"], '12.0000 SYS')''')
        self.assertEqual(
            table_EOSCHESS.json["rows"][0]["balance"], '1.0000 SYS',
            '''assertEqual(table_ALICE.json["rows"][0]["balance"], '77.0000 SYS')''')

        COMMENT('''
        Tesy Carol cannot interfere with Alice's account
        ''')
        with self.assertRaises(MissingRequiredAuthorityError):
            HOST_EOS_SUBACCOUNTS.push_action(
                "withdraw", {"from":ALICE, "amount":'1.0000 SYS', "memo": "Hello"},
                permission=(CAROL, Permission.ACTIVE),
                force_unique=True)

        COMMENT('''
        Test Alice tries to withdraw more funds than she has verify is denied
        ''')
        try:
            HOST_EOS_SUBACCOUNTS.push_action(
                "withdraw", {"from":ALICE, "amount":'2.0000 SYS', "memo": "Hello"},
                permission=(ALICE, Permission.ACTIVE),
                force_unique=True)
        except Error as ex:
            self.assertTrue(str(ex.message).find("assertion failure with message: insufficient funds available") >= 0)
        table_ALICE = HOST_EOS_SUBACCOUNTS.table("balance", ALICE)
        self.assertEqual(
            table_ALICE.json["rows"][0]["funds"], '1.0000 SYS',
            "Account balance is not zero")

        COMMENT('''
        Test Alice tries close account that has a positive balance
        ''')
        try:
            HOST_EOS_SUBACCOUNTS.push_action(
                "closeacc", {"user":ALICE},
                permission=(ALICE, Permission.ACTIVE),
                force_unique=True)
        except Error as ex:
            self.assertTrue(str(ex.message).find("assertion failure with message: Balance must be zero to close account") >= 0)
        else:
            self.assertTrue(False, "closeacc action should fail")
        table_ALICE = HOST_EOS_SUBACCOUNTS.table("balance", ALICE)
        self.assertEqual(
            table_ALICE.json["rows"][0]["funds"], '1.0000 SYS',
            "Account balance is not zero")

        COMMENT('''
        Check the after balance:
        ''')
        table_ALICE = HOST_EOSIO_TOKEN.table("accounts", ALICE)
        table_EOSCHESS = HOST_EOSIO_TOKEN.table("accounts", HOST_EOS_SUBACCOUNTS)

        self.assertEqual(
            table_ALICE.json["rows"][0]["balance"], '76.0000 SYS',
            '''assertEqual(table_ALICE.json["rows"][0]["balance"], '77.0000 SYS')''')
        self.assertEqual(
            table_EOSCHESS.json["rows"][0]["balance"], '1.0000 SYS',
            '''assertEqual(table_ALICE.json["rows"][0]["balance"], '77.0000 SYS')''')

        COMMENT('''
        Test Alice withdraw funds from her subaccount
        ''')
        HOST_EOS_SUBACCOUNTS.push_action(
            "withdraw", {"from":ALICE, "amount":'1.0000 SYS', "memo": "Hello"},
            permission=(ALICE, Permission.ACTIVE),
            force_unique=True)
        table_ALICE = HOST_EOS_SUBACCOUNTS.table("balance", ALICE)
        self.assertEqual(
            table_ALICE.json["rows"][0]["funds"], '0.0000 SYS',
            "Account balance is not zero")

        COMMENT('''
        Check the after balance:
        ''')
        table_ALICE = HOST_EOSIO_TOKEN.table("accounts", ALICE)
        table_EOSCHESS = HOST_EOSIO_TOKEN.table("accounts", HOST_EOS_SUBACCOUNTS)

        self.assertEqual(
            table_ALICE.json["rows"][0]["balance"], '77.0000 SYS',
            '''assertEqual(table_ALICE.json["rows"][0]["balance"], '77.0000 SYS')''')
        self.assertEqual(
            table_EOSCHESS.json["rows"][0]["balance"], '0.0000 SYS',
            '''assertEqual(table_ALICE.json["rows"][0]["balance"], '77.0000 SYS')''')

        COMMENT('''
        Test Carol tries close Alice's account and can't
        ''')
        with self.assertRaises(MissingRequiredAuthorityError):
            HOST_EOS_SUBACCOUNTS.push_action(
                "closeacc", {"user":ALICE},
                permission=(CAROL, Permission.ACTIVE),
                force_unique=True)
        table_ALICE = HOST_EOS_SUBACCOUNTS.table("balance", ALICE)
        self.assertEqual(
            table_ALICE.json["rows"][0]["funds"], '0.0000 SYS',
            "Account balance is not zero")

        COMMENT('''
        Test Alice can close account
        ''')
        HOST_EOS_SUBACCOUNTS.push_action(
            "closeacc", {"user":ALICE},
            permission=(ALICE, Permission.ACTIVE),
            force_unique=True)

        COMMENT('''
        Test Alice has no account:
        ''')
        table_ALICE = HOST_EOS_SUBACCOUNTS.table("balance", ALICE)
        self.assertEqual(
            len(table_ALICE.json["rows"]), 0,
            "Account balance exists")

    @classmethod
    def tearDownClass(cls):
        stop()


if __name__ == "__main__":
    unittest.main()
