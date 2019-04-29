#  Copyright (c) 2019.
#  Dremov Aleksander
#  dremov.me@gmail.com

from ParseEGE.core import Root

r = Root()

# r.parseTasks() # Not fast)
# r.parseTasks(extended=False) # Fast

r.topics = []

r.obtainImages()
r.obtainTables()