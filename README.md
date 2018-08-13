### Introduction
This repo consists of utilities for doing conditional airdrops for purposes such as distribution of bonuses, bounties, rewards and dividends on the ethereum blockchain. 

rewarder.py is a python utility for distributing tokens to ethereum addresses based on a specified rewards criteria sql 

dividends.py is a python utility for distributing tokens to ethereum addresses based on their holding a specific token. 

both utilities ensure reward distributions is not repeated for the same address twice for the same run and logs txid's and distribution info to a postgres db.

### Declare below Environment Variables before running.
```
export GETH_NODE_URL=https://ropsten.infura.io/v3/YOURAPIKEY
export token_owner_private_key=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

```
### Example run for rewarder.py

```
$ ./rewarder.py
Usage : ./rewarder.py Token Amount Run

Below example distributed 1000 EST tokens 

$ ./rewarder.py EST 1000 10
Reward for run 10 not found for 0xa03783510256f318ad666354c39db15d8b2f516a adding to tse_rewards table
Reward for run 10 not found for 0x6641c30B8Ec57A6168707115b80B0af1a5cf160C adding to tse_rewards table

Rewarding EST to 0xa03783510256f318ad666354c39db15d8b2f516a txid is  b'\x1b\xd1\xc2\x9a\xa1\x06\x08\xb0]Q\xd2\x1e\x7f\x87\xc1\xff3\xa8\x8cX/\xb9\xf02\xc4\xd3c\xd9\xe7\x08\r%'
Rewarding EST to 0x6641c30B8Ec57A6168707115b80B0af1a5cf160C txid is  b't\xb1\xcb\xda8\xdd\nbs\xf35\x9c\xde\x14\xcb\x08Z\xac\xd8\x8enE\xa9m\xb2\xb0\xf1\xbaZU#\xcf'

$ ./rewarder.py EST 1000 10
Reward for run 10 already distributed to 0xa03783510256f318ad666354c39db15d8b2f516a
Reward for run 10 already distributed to 0x6641c30B8Ec57A6168707115b80B0af1a5cf160C
```

### Example run for dividends.py 

Below example gives ES5 token holders an extra 50% based on their ES5 token holding. This can also be used to give a different droptoken based on the basetoken holding as long as the token distributing address has sufficient balance for the drop token. The amounts shown below are in wei (10^18)

```
$ ./dividends.py 
Usage : ./dividends.py BaseToken DropToken Ratio Run

$ ./dividends.py ES5 ES5 0.5 2
Reward for run 2 not found for 0x3A514B826d8235DfBFc7e67F9D7F6173E9C109Ed adding to tse_dividends table
Reward for run 2 not found for 0x6641c30B8Ec57A6168707115b80B0af1a5cf160C adding to tse_dividends table

Rewarding 5500000000000000000 ES5 to 0x3A514B826d8235DfBFc7e67F9D7F6173E9C109Ed txid is  b'W\xe6\xbf\x00j\xfbI\xfc\xb7\x7f\x00|I\xa2\x96\x8eXZ\xc2i\xbb\x99>`\xa9(-\xb7\xfbH\xd0J'
Rewarding 430650000000000000000 ES5 to 0x6641c30B8Ec57A6168707115b80B0af1a5cf160C txid is  b'\x88\xc5/\xbc\xf31&\xab\xf0i\xa6\xf8h\x91D\x82\xc1\x03w\xd3\xe4"\x00\x97\xf0\xf2H\x11C\xd9E\xfc'

$ ./dividends.py ES5 ES5 0.5 2
Reward for run 2 already distributed to 0x3A514B826d8235DfBFc7e67F9D7F6173E9C109Ed
Reward for run 2 already distributed to 0x6641c30B8Ec57A6168707115b80B0af1a5cf160C

```



