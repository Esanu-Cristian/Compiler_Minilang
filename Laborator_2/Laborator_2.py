import re

class CatAutomaton:
    def __init__(self):
        self.states = ['q0', 'q1', 'q2', 'q3']
        self.start_state = 'q0'
        self.final_state = 'q3'
        self.current_state = self.start_state

    def transition(self, char):
        if self.current_state == 'q0':
            if char == 'c':
                self.current_state = 'q1'
            else:
                self.current_state = 'q0'
        elif self.current_state == 'q1':
            if char == 'a':
                self.current_state = 'q2'
            elif char == 'c':
                self.current_state = 'q1'
            else:
                self.current_state = 'q0'
        elif self.current_state == 'q2':
            if char == 't':
                self.current_state = 'q3'
            elif char == 'c':
                self.current_state = 'q1'
            else:
                self.current_state = 'q0'
        elif self.current_state == 'q3':
            self.current_state = 'q3'

    def process(self, text):
        self.current_state = self.start_state
        for char in text:
            self.transition(char)
        return self.current_state == self.final_state

def contains_cat(text):
    automaton = CatAutomaton()
    for i in range(len(text)):
        if automaton.process(text[i:]):
            return True
    return False

class FormalAutomaton:
    def __init__(self):
        self.states = ['q0', 'q1', 'q2', 'q3']
        self.start_state = 'q0'
        self.final_state = 'q3'
        self.current_state = self.start_state

    def transition(self, char):
        if self.current_state == 'q0':
            if char == 'a':
                self.current_state = 'q1'
            else:
                self.current_state = 'q0'
        elif self.current_state == 'q1':
            if char == 'b':
                self.current_state = 'q2'
            else:
                self.current_state = 'q1'
        elif self.current_state == 'q2':
            if char == 'c':
                self.current_state = 'q3'
            else:
                self.current_state = 'q2'
        elif self.current_state == 'q3':
            self.current_state = 'q3'

    def process(self, word):
        self.current_state = self.start_state
        for char in word:
            self.transition(char)
        return self.current_state == self.final_state

def generate_L():
    alphabet = ['a', 'b', 'c']
    words = []
    for a in alphabet:
        for b in alphabet:
            for c in alphabet:
                for d in alphabet:
                    for e in alphabet:
                        for f in alphabet:
                            word = a + b + c + d + e + f
                            if sum(word.count(x*2) for x in alphabet) == 3:
                                words.append(word)
    return words

def verify_words():
    automaton = FormalAutomaton()
    test_words = ['aabbcc', 'abbcac', 'bbbaac']
    for word in test_words:
        result = automaton.process(word)
        print(f"Word '{word}' is in L: {result}")

def verify_invoice(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    client_regex = r"Client:\s+\w+"
    product_regex = r"Produs:\s+\w+"
    price_regex = r"Pret:\s+\d+(\.\d{2})?"
    tva_regex = r"TVA:\s+\d+(\.\d{2})?"
    qty_regex = r"Cantitate:\s+\d+"

    errors = []
    if not re.search(client_regex, content):
        errors.append("Informatii client lipsa sau format gresit.")
    if not re.search(product_regex, content):
        errors.append("Detalii produs lipsa sau format gresit.")
    if not re.search(price_regex, content):
        errors.append("Pret lipsa sau format gresit.")
    if not re.search(tva_regex, content):
        errors.append("TVA lipsa sau format gresit.")
    if not re.search(qty_regex, content):
        errors.append("Cantitate lipsa sau format gresit.")

    if errors:
        print("Erori detectate in factura:")
        for err in errors:
            print(err)
    else:
        print("Factura respecta formatul.")


if __name__ == "__main__":
    # Pr 1, 2
    text = "the cat sat on the mat"
    print(f"Textul contine 'cat': {contains_cat(text)}")

    # Pr 3
    verify_words()

    # Pr 4
    verify_invoice("factura.txt")
