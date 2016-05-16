import pexpect

class CoqTop:
    def __init__(self, coqtop_bin="coqtop", color=False, args=None):
        self.coqtop_bin = coqtop_bin
        self.args = (args or [])
        if color:
            self.args.extend(["-color", "on"])
        self.coqtop = None

    def __enter__(self):
        if self.coqtop:
            raise ValueError("Nested Coqtop contexts")
        self.coqtop = pexpect.spawn(self.coqtop_bin, args=self.args, echo=False, encoding="utf-8")
        self.next_prompt()
        return self

    def __exit__(self, type, value, traceback):
        self.coqtop.kill(9)

    def next_prompt(self):
        COQTOP_PROMPT = "\r\n[^< ]+ < "
        self.coqtop.expect(COQTOP_PROMPT, timeout = 1)
        return self.coqtop.before

    def sendline(self, line):
        line = line.strip()
        print("Sending {}".format(line))
        self.coqtop.sendline(line)
        return self.next_prompt()

def sendlines(*lines):
    with CoqTop() as coqtop:
        for line in lines:
            print("=====================================")
            print(line)
            print("-------------------------------------")
            response = coqtop.sendline(line)
            print(response)

# Process the document, and then do another pass on it to add the output.
def main():
    sendlines("Goal False -> True.", "Proof.", "intros H.",
              "Check H.", "Chchc.", "apply I.", "Qed.")

if __name__ == '__main__':
    main()
