#!/usr/bin/python3
import psycopg2, sys, os, web3, json
from web3 import Web3, HTTPProvider

# Map runtime inputs
if len(sys.argv) != 4 :
    print ("Usage :", sys.argv[0], "Token Amount Run")
    sys.exit()

token = sys.argv[1]
amount = int(sys.argv[2])
run = int(sys.argv[3])
    
# Connect to DB
conn = psycopg2.connect(database="tradingdb", user = "web", password = "password", host = "localhost", port = "5432")
conn.autocommit = True
cur = conn.cursor()

# If table doesnt exist create

createtablesql = """ CREATE TABLE IF NOT EXISTS public.tse_rewards
(
    eth_address character varying(42) COLLATE pg_catalog."default" NOT NULL,
    token character varying(5) COLLATE pg_catalog."default" NOT NULL,
    amount numeric,
    run numeric,
    txid character varying(66) COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.tse_rewards
    OWNER to web;

"""

cur.execute(createtablesql)

# Obtain token symbol from tse_project table
cur.execute ("SELECT token_contract_address FROM tse_project WHERE token_symbol = %s", (token,));
tokenaddress = Web3.toChecksumAddress(cur.fetchone()[0])

# Obtain list of ethereum accounts based on criteria sql
criteria="SELECT DISTINCT eth_address FROM user_accounts_profile WHERE verified=true"
cur.execute (criteria)
rows = cur.fetchall()

# For every ethereum address selected, check if they have not recieved rewards for this run already and if not then onboard accordingly.
for row in rows:
    cur.execute ("SELECT eth_address,run,txid FROM tse_rewards WHERE eth_address = %s AND token = %s AND run = %s AND txid IS NOT NULL" , (row[0], token, run, ));
    if (cur.rowcount == 0) :
        print ("Reward for run", run, "not found for", row[0], "adding to tse_rewards table")
        cur.execute ("INSERT INTO tse_rewards (eth_address, token, amount, run) VALUES (%s , %s, %s, %s)", (row[0], token, amount, run))
    else :
        print ("Reward for run", run, "already distributed to", row[0])

# Connect to GETH node
GETH_NODE_URL=os.environ.get('GETH_NODE_URL', '')
web3 = Web3(HTTPProvider(GETH_NODE_URL))

# Uncomment below 2 lines if Connecting to a POA chain such as Rinkeby or Geth in dev mode
#from web3.middleware import geth_poa_middleware
#web3.middleware_stack.inject(geth_poa_middleware, layer=0)

# Create TokenInstance with Token Address & ABI
with open('token.json', 'r') as abi_definition:
    abi = json.load(abi_definition)
    
tokeninst = web3.eth.contract(
    address=tokenaddress, 
    abi=abi, 
)

token_owner_private_key = os.environ.get('token_owner_private_key', '')
token_owner = web3.eth.account.privateKeyToAccount(token_owner_private_key).address
nonce = web3.eth.getTransactionCount(token_owner)

# Distribute rewards to eligible ethereum addresses
cur.execute ("SELECT DISTINCT eth_address, amount FROM tse_rewards WHERE run = %s AND token = %s AND txid IS NULL", (run, token));
rows = cur.fetchall()
for row in rows:    
    dropaddress = web3.toChecksumAddress(row[0])
    qty = (amount*10**18)
    
    txn = tokeninst.functions.transfer(dropaddress, qty)
    
    txn = txn.buildTransaction({
            'gas': 51000,
            'nonce': nonce,
        })

    txn = web3.eth.account.signTransaction(txn, token_owner_private_key)
    txid = web3.eth.sendRawTransaction(txn.rawTransaction)
        
    print ("Rewarding", token, "to", row[0] , "txid is " , txid.decode("utf8"))
    cur.execute("UPDATE tse_rewards SET txid = (%s) WHERE eth_address = (%s) AND token = (%s) AND run = %s", (txid, row[0], token, run));
    nonce = nonce + 1 

conn.close()
