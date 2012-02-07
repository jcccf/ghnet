from misc import *
db = MDb.MDb('ghnet', host='localhost', username='ghnet', password='ghnet87')

MGraph.draw_fork_trees(db)