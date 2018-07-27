### Introduction
rewarder.py is a python utility for distributing tokens to ethereum addresses based on a specified rewards criteria sql. It ensures the same airdrop is not repeated for the same address twice and logs txid's.

### Usage
./rewarder.py tokensymbol amount run

### Example
```
$ ./rewarder.py EST 1000 10
Reward for run 10 not found for 0xa03783510256f318ad666354c39db15d8b2f516a adding to tse_rewards table
Reward for run 10 not found for 0x6641c30B8Ec57A6168707115b80B0af1a5cf160C adding to tse_rewards table

Rewarding EST to 0xa03783510256f318ad666354c39db15d8b2f516a txid is  b'\x1b\xd1\xc2\x9a\xa1\x06\x08\xb0]Q\xd2\x1e\x7f\x87\xc1\xff3\xa8\x8cX/\xb9\xf02\xc4\xd3c\xd9\xe7\x08\r%'
Rewarding EST to 0x6641c30B8Ec57A6168707115b80B0af1a5cf160C txid is  b't\xb1\xcb\xda8\xdd\nbs\xf35\x9c\xde\x14\xcb\x08Z\xac\xd8\x8enE\xa9m\xb2\xb0\xf1\xbaZU#\xcf'

$ ./rewarder.py EST 1000 10
Reward for run 10 already distributed to 0xa03783510256f318ad666354c39db15d8b2f516a
Reward for run 10 already distributed to 0x6641c30B8Ec57A6168707115b80B0af1a5cf160C
```

### Declare below Environment Variables before running.
```
export GETH_NODE_URL=https://ropsten.infura.io/v3/YOURAPIKEY
export token_owner_private_key=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Note : Please refer to criteria & dbtable in the script should you wish to reward using any other desired criteria.


### TODO
- Introduce rewards based on holding other tokens by checking reciever addresses token balances.
