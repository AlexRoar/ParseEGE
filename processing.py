#  Copyright (c) 2019.
#  Dremov Aleksander
#  dremov.me@gmail.com

from ParseEGE.core import Root

r = Root()
# r = Root(service='hist-ege', workdir='ParseEGE/data-history') #What about history?

r.topics = []  # custom topics for parsing (empty == all)
r.parseTasks(True, False, False)  # Not fast, but with additional data

# r.parseTasks(extended=False) # Fast (but still not too fast)
# r.directParseQuestion('15618')
# r.parseOneTopic(316)

# r.obtainImages()
# r.obtainTables()
