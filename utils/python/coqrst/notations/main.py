

def sphinxify(notation):
    vs = visitors.TacticNotationsToDotsVisitor()
    vs.visit()

