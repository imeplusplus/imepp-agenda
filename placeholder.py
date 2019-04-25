from bot_db import db

db['links'].upsert(dict(url='http://bit.ly/imepp-2019-upsolving-h0', name='HW0'), ['url'])
db['links'].upsert(dict(url='http://bit.ly/imepp-2019-upsolving-h1', name='HW1'), ['url'])
db['links'].upsert(dict(url='http://bit.ly/imepp-2019-upsolving-h2', name='HW2'), ['url'])
