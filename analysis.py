from newProgram import *
# define enum for different types of statements
SUBSPACE = 1
SUBSPACE_WITH_SIG = 2
class analyser:
    def __init__(self, n, program:newProgram,  type=SUBSPACE, sig=None):
        self.n = n
        self.program = program
        self.type = type
        self.sig = sig
        if type == SUBSPACE:
            self.state = np.eye(2**n)
        if type == SUBSPACE_WITH_SIG:
            self.state = [np.eye(2**i) for i in sig]

    def abstract_interpret(self):
        # step1 build the control flow graph
        locations = []
        for i in range(len(self.program.statements)):
            if self.program.statements[i].type == "label":
                locations.append(i)
        