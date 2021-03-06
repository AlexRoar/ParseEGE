# ParseEGE

Basic usage:

```python
from ParseEGE.core import Root

# services:
# inf = inf-ege
# history = hist-ege

# r = Root(workdir='dir to save files', service='service')

r = Root() # Default - informatics

r.parseTasks(extended=True, doNotLoadDB=False, saveInLoop=True)

r.topics = [] # custom topics. Empty = all

r.obtainImages() # collect images from tasks
r.obtainTables() # collect tables from tasks (works bad)
```
## Installation

Currently, the package cannot be installed by pip, and I don't think that it is really needed.
So, to install this package, just download repository, install requirements using pip from requirments.txt, and that's all.

#How does it work ?
It generates a base of all questions in a usable format. User-friendly interface to access data is now in work.

# Root.__init__ params:
**workdir** - relative path to package workdir default = ParseEGE/data/

**service** - service string ('inf-ege', 'chem-ege')
Service id can be found in the URL:

https://inf-ege.sdamgia.ru

https://chem-ege.sdamgia.ru


# Root.parseTasks() params:
**extended** - include or not raw HTML data and sources of task.

**doNotLoadDB** - if true, it will not load old DB, but overwrite it.

**saveInLoop** - save data during the process or save only in the end.

# Root.obtainImages()

It will collect images from questions of selected topics. Script saves images in **workdir**/**service**/img/**ege task number**/**task number**

Ex: ParseEGE/data/inf-ege/img/1/136/image_DDK7.svg

# Root.obtainTables()

It will collect tables from questions of selected topics. Script saves images in **workdir**/**service**/tables/**ege task number**/**task number**

**It works properly only in several cases (tasks № 2, 12, and others)**

Ex: ParseEGE/data/inf-ege/tables/2/9353/table_5CVD.png

# Topics

The topic is the last param in the request:

https://chem-ege.sdamgia.ru/test?theme=150 - 150

https://inf-ege.sdamgia.ru/test?theme=275 - 275

# Parsed versions

The full parsed version of informatics can be found in ParseEGE/save-inf/parsed.json

# Warning

This package has not been tested properly on everything besides informatics. Feel free to report about errors

# Drawbacks

Do not use text representation of solution or question if it contains tables. Use raw HTML data and render it manually. You can try to generate images of tables using method obtainTables(), but it works properly only in certain cases.
