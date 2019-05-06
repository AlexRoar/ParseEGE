#  Copyright (c) 2019.
#  Dremov Aleksander
#  dremov.me@gmail.com

from ParseEGE.core import Root

# services:
# inf = inf-ege
# history = hist-ege
# r = Root(workdir='dir to save files', service='service')

r = Root() # Default - informatics

r.parseTasks(extended=True, doNotLoadDB=False, saveInLoop=True)
# r.parseTasks(extended=False) # Fast

r.topics = []

r.obtainImages()
r.obtainTables()