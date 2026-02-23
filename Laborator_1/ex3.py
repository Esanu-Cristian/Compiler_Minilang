def afiseaza_palindroame():
    alfabet = ['0', '1', '2']

    for lungime in range(1, 6):
        print(f"\nNivel (Lungime {lungime}):")
        palindroame = []
        jumate_lungime = (lungime + 1) // 2

        # Generare explicita pentru fiecare lungime
        if jumate_lungime == 1:
            for a in alfabet:
                jumate = a
                if lungime % 2 == 0:
                    palindrom = jumate + jumate[::-1]
                else:
                    palindrom = jumate + jumate[:-1][::-1]
                palindroame.append(palindrom)
        elif jumate_lungime == 2:
            for a in alfabet:
                for b in alfabet:
                    jumate = a + b
                    if lungime % 2 == 0:
                        palindrom = jumate + jumate[::-1]
                    else:
                        palindrom = jumate + jumate[:-1][::-1]
                    palindroame.append(palindrom)
        elif jumate_lungime == 3:
            for a in alfabet:
                for b in alfabet:
                    for c in alfabet:
                        jumate = a + b + c
                        if lungime % 2 == 0:
                            palindrom = jumate + jumate[::-1]
                        else:
                            palindrom = jumate + jumate[:-1][::-1]
                        palindroame.append(palindrom)

        print(", ".join(palindroame))
        print(f"Total palindroame pe nivelul {lungime}: {len(palindroame)}")

afiseaza_palindroame()
