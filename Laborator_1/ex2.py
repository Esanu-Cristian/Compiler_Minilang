def concat(s1, s2):
    return s2 + s1

def repeat(s, n):
    return s * n

def reverse_op(s):
    return s[::-1]

def extract(s, i, j):
    return s[i:j+1]

def replace_op(s, sub, new_sub):
    return s.replace(sub, new_sub, 1)

def aplica_toate_operatiile(cuvant):
    print(f"\n--- Aplicare operatii pentru cuvantul: '{cuvant}' ---")
    
    print(f"Concatenare (adauga 'X' la finalul lui '{cuvant}'): {concat('X', cuvant)}")
    print(f"Repetare (de 3 ori): {repeat(cuvant, 3)}")
    print(f"Inversare: {reverse_op(cuvant)}")
    
    if len(cuvant) >= 3:
        print(f"Extractie (pozitiile 0-2): {extract(cuvant, 0, 2)}")
    
    prima_litera = cuvant[0]
    print(f"Inlocuire (prima '{prima_litera}' cu 'Y'): {replace_op(cuvant, prima_litera, 'Y')}")

aplica_toate_operatiile("abdcx12")