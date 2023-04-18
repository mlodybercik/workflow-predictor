# Mini raport z analiz

<em> To jest mini raport z analizy danych, proszę dopisywać tu wnioski z przeprowadzonych analiz </em>

## *hac-run-id* a *business-day*

Jak sie okazuje, *hac-run-id* jest dosłownym zmapowaniem wartości *business-day*. 
```
hac-run-id = 1
business-day = 0

hac-run-id = 2
business-day = 1
```

W przypadku wystąpienia wartości null w atrybucie *business-day*, *hac-run-id- przyjmie wartość -9.

### Wnioskując
Jest to wartość redundantna, której możemy się pozbyć.


## Czym jest *parent-uid*?
Nie wiem

## Analiza business-day
Zdecydowana wiekszosc zadan jest realizowana przez 90% dni miesiaca w tym samym business-day, a dopiero
pod koniec miesiaca (ostatnie 3/4 dni) zadania sa wrzucane w rozne BD. Co ciekawe, przez te 90% miesiaca 
business-day to BD0 lub BD5.
### Interpretacja
Dlaczego BD5?

## Zależność czasu wykonywania się zadań od daty
Ze wstępnej analizy wyszło, że na końcu miesiąca na raz wykonuje się bardzo dużo jobów, przez co czas potrzebny na wykonanie ich rośnie proporcjonalnie (to może być nawet 10x przyrost)