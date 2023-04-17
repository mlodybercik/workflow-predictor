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
