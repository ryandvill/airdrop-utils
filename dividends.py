#!/usr/bin/python3
import psycopg2, sys, os, web3, json,decimal
from web3 import Web3, HTTPProvider
from decimal import Decimal

# Map runtime inputs
if len(sys.argv) != 5 :
    print ("Usage :", sys.argv[0], "BaseToken DropToken Ratio Run")
    sys.exit()

basetoken = sys.argv[1]
droptoken = sys.argv[2]
ratio = Decimal(sys.argv[3])
run = int(sys.argv[4])
    
# Connect to DB
conn = psycopg2.connect(database="tradingdb", user = "web", password = "password", host = "localhost", port = "5432")
conn.autocommit = True
cur = conn.cursor()

# If table doesnt exist create
createtablesql = """ CREATE TABLE IF NOT EXISTS public.tse_dividends
(
    eth_address character varying(42) COLLATE pg_catalog."default" NOT NULL,
    basetoken character varying(5) COLLATE pg_catalog."default" NOT NULL,
    droptoken character varying(5) COLLATE pg_catalog."default" NOT NULL,
    ratio numeric,
    dropqty numeric,
    run numeric,
    txid character varying(66) COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.tse_dividends
    OWNER to web;

"""

cur.execute(createtablesql)

# Obtain token symbols from tse_project table
cur.execute ("SELECT token_contract_address FROM tse_project WHERE token_symbol = %s", (basetoken,));
basetokenaddress = Web3.toChecksumAddress(cur.fetchone()[0])

cur.execute ("SELECT token_contract_address FROM tse_project WHERE token_symbol = %s", (droptoken,));
droptokenaddress = Web3.toChecksumAddress(cur.fetchone()[0])

# Connect to GETH node
GETH_NODE_URL=os.environ.get('GETH_NODE_URL', '')
web3 = Web3(HTTPProvider(GETH_NODE_URL))

# Create TokenInstances with Token Address & ABI

with open('token.json', 'r') as abi_definition:
    abi = json.load(abi_definition)
    
basetokeninst = web3.eth.contract(
    address=basetokenaddress, 
    abi=abi, 
)

droptokeninst = web3.eth.contract(
    address=droptokenaddress, 
    abi=abi, 
)

token_owner_private_key = os.environ.get('token_owner_private_key', '')
token_owner = web3.eth.account.privateKeyToAccount(token_owner_private_key).address
nonce = web3.eth.getTransactionCount(token_owner)

# Obtain list of ethereum accounts based on criteria sql
criteria="SELECT DISTINCT eth_address FROM user_accounts_profile WHERE verified=true"
cur.execute (criteria)
rows = cur.fetchall()

# Verify if addresses hold baseaddress tokens and how much
for row in rows:
    balance = basetokeninst.call().balanceOf(row[0])
    if (balance > 0) :
        dropqty = balance * ratio
        cur.execute ("SELECT eth_address,run,txid FROM tse_dividends WHERE eth_address = %s AND basetoken = %s AND droptoken = %s AND run = %s AND txid IS NOT NULL" , (row[0], basetoken, droptoken, run, ));
        if (cur.rowcount == 0) :
            print ("Reward for run", run, "not found for", row[0], "adding to tse_dividends table")
            cur.execute ("INSERT INTO tse_dividends (eth_address, basetoken, droptoken, ratio, dropqty, run) VALUES (%s , %s, %s, %s, %s, %s)", (row[0], basetoken, droptoken, ratio, dropqty, run))
        else :
            print ("Reward for run", run, "already distributed to", row[0])


# Distribute rewards to eligible ethereum addresses
cur.execute ("SELECT DISTINCT eth_address, dropqty FROM tse_dividends WHERE run = %s AND basetoken = %s AND droptoken = %s AND txid IS NULL", (run, basetoken, droptoken));
rows = cur.fetchall()
for row in rows:    
    dropaddress = web3.toChecksumAddress(row[0])
    dropqty = int(row[1])
    txn = droptokeninst.functions.transfer(dropaddress, dropqty)
    
    txn = txn.buildTransaction({
            'gas': 51000,
            'nonce': nonce,
        })

    txn = web3.eth.account.signTransaction(txn, token_owner_private_key)
    txid = web3.eth.sendRawTransaction(txn.rawTransaction)
        
    print ("Rewarding", dropqty, droptoken, "to", row[0] , "txid is " , txid)
    cur.execute("UPDATE tse_dividends SET txid = (%s) WHERE eth_address = (%s) AND basetoken = (%s) AND droptoken = %s AND run = %s", (txid, row[0], basetoken, droptoken, run));
    nonce = nonce + 1 

conn.close()
