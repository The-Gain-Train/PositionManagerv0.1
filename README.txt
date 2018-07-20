Input file must remain in same directory as fulltest.py

Input file must be filled out as follows:

A		B		C		D
Market  	OrderQty	StopPrice	TargetPrice   (prices in sats!)

EXAMPLE:

	A		B		C		D
1	MFT		10000		0.00000180	0.00000750
2	SNT		4700		0.00000950	0.00002500
3	XVG		50000		0.00000050	0.00001000


Field A is the crypto symbol (do NOT include -BTC)
Field B is trade size (quantity)
Field C is stop loss level in sats
Field D is target level in sats

Run the main program which is currently set to cycle every 20 seconds
- Each cycle will check pricing of assets in the input file
- Logic will then determine if action needs to be taken on any asset
