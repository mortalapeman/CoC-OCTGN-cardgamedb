import json

from octgn import *
from os.path import sep
from IPython.core.debugger import Tracer; bp = Tracer()

path = sep.join(['.', 'data', 'cards-7-28-12.json'])
data = json.load(open(path, 'r'))

cardsetnames = set([x['setname'] for x in data])
fac = CoCCardFactory()

for name in cardsetnames:
    cset = CoCCardSet(name)
    dest = sep.join(['.', 'data'])
    for i, d in enumerate(filter(lambda x: x['setname'] == name, data)):
        card = fac.create(cset.setid, d, i + 1)
        cset.addcard(card)
    print 'writing set: %s' % (name)
    cset.write(dest)
print 'Finished!'
