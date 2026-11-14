# Notatki do dokumentacji i sprawozdania

Zebrane fakty, decyzje i wyniki do przeniesienia do dokumentacji projektu i sprawozdania.
Liczby policzone na pełnym zbiorze (95 samochodów, bez filtrów) w wersji aplikacji z 14.11.2026.

## 1. Dane

### Źródło

- Zbiór **Qatar Cars**, Paul Musgrave, 2025, licencja **CC BY 4.0**: https://github.com/profmusgrave/qatarcars
- Do cytowania: Paul Musgrave, "Defaulting to Inclusion: Producing Sample Datasets for the Global Data Science Classroom", *Journal of Political Science Education*, 2025, doi:10.1080/15512169.2025.2572320.
- Dane zebrane w styczniu 2025 r., głównie z serwisu YallaMotors Qatar. Opisują rynek katarski, nie polski.
- Plik: `data/qatarcars.csv`, pobrany 14.11.2026.

### Od surowego pliku do analizowanego zbioru

| Krok | Liczba samochodów |
| --- | --- |
| Surowy plik CSV | 105 |
| Pominięte auta elektryczne (brak zużycia paliwa w źródle) | -10 |
| **Zbiór analizowany** | **95** (27 marek) |

Pominięte auta elektryczne: Mercedes EQS, Hyundai Ioniq 5, Kia EV9, Jaguar I-Pace, Lotus Evija, Tesla Model X, Model Y, Model 3, BYD Seal, BYD Atto 3.

Skład zbioru po filtrze:

- napęd: benzyna 81, hybryda 14;
- nadwozie: SUV 48, sedan 26, coupe 13, hatchback 8;
- kraj marki: Japonia 29, Niemcy 19, Chiny 16, Wielka Brytania 9, Korea Płd. 8, USA 6, Włochy 5, Szwecja 3.

Wymaganie projektu (min. 30 obiektów, min. 5 atrybutów) jest spełnione z zapasem.

### Atrybuty

| Atrybut | Jednostka | Kolumna w CSV | Uwagi |
| --- | --- | --- | --- |
| Moc | KM | `horsepower` | |
| Spalanie | l/100 km | `economy` | |
| Bagażnik | l | `trunk` | patrz "Jakość danych" |
| Cena | PLN | `price` | przeliczona z QAR |
| Przyspieszenie 0-100 km/h | s | `performance` | zamiast prędkości maksymalnej |

### Decyzje dotyczące danych (do uzasadnienia w dokumentacji)

1. **Przyspieszenie 0-100 km/h zamiast prędkości maksymalnej.** Temat projektu wymienia prędkość maksymalną, ale żaden darmowy zbiór nie miał wszystkich pięciu atrybutów naraz (szczególnie rzadkie były bagażnik i prędkość maksymalna). Qatar Cars ma cztery z pięciu, a przyspieszenie opisuje tę samą cechę (osiągi). *Warto potwierdzić u prowadzącego.*
2. **Pominięcie aut elektrycznych.** Źródło nie podaje dla nich zużycia paliwa, a l/100 km nie ma dla nich sensu.
3. **Przeliczenie cen na PLN.** Ceny w źródle są w rialach katarskich (QAR, 2025). Kurs: średni kurs NBP **1,1354 PLN/QAR**, tabela B nr 002/B/NBP/2025 z 15.01.2025 (miesiąc zebrania danych). Ceny zaokrąglone do pełnych złotych. Przeliczenie liniowe nie zmienia skośności, kurtozy, współczynnika zmienności ani korelacji.
4. **Rok modelowy 2025** przypisany wszystkim autom (zbiór opisuje rynek ze stycznia 2025).

### Jakość danych (ograniczenia do opisania)

- **Bagażnik 0 l** w 4 autach: Bugatti Centodieci, McLaren Senna, 720S, Artura. To raczej brak danych niż prawdziwa pojemność. Z tego powodu dominanta bagażnika wynosi 0 l.
- **Podejrzanie małe bagażniki** w autach, które w rzeczywistości mają duże: BMW serii 3 (59 l), Volvo XC90 (71 l), XC60 (71 l), XC40 (54 l), Jetour X70 Plus (57 l), Lexus RC F (66 l). Prawdopodobnie błędy w źródle. Zostawione bez zmian, bo poprawianie wymagałoby weryfikacji każdego auta.
- **Hybrydy plug-in oznaczone jako benzynowe** mają bardzo niskie spalanie katalogowe (np. McLaren Artura 4,6 l/100 km, Lynk & Co 08 EM-P). To wpływa na ranking.
- **Wartości skrajne cen i mocy**: Bugatti Centodieci (37,5 mln PLN, 1600 KM), Bugatti Chiron (14,9 mln PLN, 1578 KM), McLaren Senna (5,7 mln PLN, 800 KM). Według reguły Q3 + 1,5 IQR odstających cen jest 11 (powyżej ok. 640 tys. PLN).

## 2. Przechowywanie danych

- **SQLite**, jedna tabela `cars`, obsługiwana przez SQLAlchemy.
- Kolumny: `id`, `brand`, `model`, `variant`, `year`, pięć atrybutów (`power`, `fuel`, `trunk`, `price`, `acceleration`), `source_url`, `source_date`.
- **Ograniczenia w bazie**:
  - `CHECK`: wszystkie atrybuty > 0, bagażnik >= 0, rok 1900-2100;
  - `UNIQUE (brand, model, variant, year)`: jedno auto w jednej wersji występuje raz.
- Import przy pierwszym uruchomieniu z pustą bazą, wsadowo i w jednej transakcji, z pominięciem już zapisanych aut (`INSERT ... ON CONFLICT DO NOTHING`). Ponowne uruchomienie nie tworzy duplikatów.
- Plik CSV jest źródłem prawdy, a baza jest odtwarzana z niego przy starcie kontenera.

**Uzasadnienie wyboru SQLite** (wymaganie "dobrać formę przechowywania"): mały zbiór (95 rekordów), jeden użytkownik, dane tylko do odczytu po imporcie. Baza plikowa daje strukturę relacyjną z typami i ograniczeniami bez osobnego serwera. Wcześniejsza wersja projektu używała PostgreSQL; zmiana uprościła uruchamianie (jeden kontener zamiast dwóch) bez utraty niczego, czego projekt potrzebuje.

## 3. Aplikacja

- Python 3.12, **Streamlit** (interfejs), **pandas** i **SciPy** (obliczenia), **Plotly** (wykresy), **SQLAlchemy** (baza).
- Uruchamianie: Docker i Task, `task dev`, adres http://localhost:8501. Zmiany w `src/` przeładowują aplikację automatycznie.
- Pięć atrybutów jest zdefiniowanych w jednym miejscu (`src/attributes.py`): nazwa, jednostka, kierunek "mniej = lepiej", liczba miejsc po przecinku, jednostka piktogramu. Z tej definicji powstają kolumny bazy, statystyki, ranking i wykresy.
- Liczby wyświetlane w polskim zapisie (spacja jako separator tysięcy, przecinek dziesiętny).

Zakładki:

| Zakładka | Zawartość | Wymaganie |
| --- | --- | --- |
| Samochody | tabela wszystkich aut z pięcioma atrybutami | prezentacja danych |
| Statystyki | tabela miar rozkładu, histogram z wykresem pudełkowym | miary rozkładu |
| Porównania | wykres rozrzutu dwóch atrybutów, piktogram ("garaż obrazkowy") | wykresy obrazkowe |
| Korelacje | macierz Pearsona lub Spearmana jako mapa ciepła i tabela, wnioski | korelacje każdej pary |
| Ranking | ranking aut według wag ustawionych przez użytkownika | "nietypowo i użytecznie" |

Panel boczny: źródło danych oraz filtry marki i maksymalnej ceny. Wszystkie obliczenia dotyczą aktualnego wyboru; przy mniej niż 30 autach aplikacja wyświetla ostrzeżenie.

## 4. Metody

### Miary rozkładu

| Grupa (wymaganie) | Miary |
| --- | --- |
| Tendencja centralna | średnia, mediana, dominanta |
| Zróżnicowanie | minimum, maksimum, rozstęp, Q1, Q3, IQR, wariancja, odchylenie standardowe, współczynnik zmienności |
| Asymetria | współczynnik skośności |
| Koncentracja | kurtoza nadmiarowa |

Szczegóły do opisania:

- **Wariancja i odchylenie standardowe z próby** (dzielnik n-1).
- **Kwartyle** metodą interpolacji liniowej (domyślna w pandas).
- **Współczynnik zmienności** = odchylenie standardowe / średnia * 100%.
- **Skośność**: skorygowany współczynnik Fishera-Pearsona (SciPy `skew(bias=False)`), wymaga co najmniej 3 obserwacji.
- **Kurtoza nadmiarowa** (rozkład normalny = 0), skorygowana (SciPy `kurtosis(fisher=True, bias=False)`), wymaga co najmniej 4 obserwacji. W polskich podręcznikach kurtoza jest klasyfikowana jako miara koncentracji. Alternatywą byłby współczynnik Giniego z krzywą Lorenza (niezaimplementowane).
- **Dominanta**: najczęstsza wartość; przy remisie wyświetlane są wszystkie, gdy żadna wartość się nie powtarza: "Brak". Przy danych ciągłych (cena) dominanta z pojedynczych wartości jest mało informatywna (patrz "Otwarte kwestie").
- Miara nieokreślona (np. skośność dla 1 auta) wyświetla się jako "-".

### Korelacje

- **Pearson** (zależność liniowa) i **Spearman** (zależność monotoniczna, na rangach), do wyboru w aplikacji.
- Wymagane co najmniej 3 obserwacje; dla stałego atrybutu współczynnik jest nieokreślony.
- Aplikacja wskazuje parę o największej wartości bezwzględnej współczynnika.

### Ranking

1. Każdy atrybut normalizowany min-max do przedziału 0-1 w obrębie aktualnego wyboru.
2. Dla spalania, ceny i przyspieszenia skala odwrócona (1 - wartość), bo mniej znaczy lepiej.
3. Wynik = średnia ważona znormalizowanych atrybutów * 100. Wagi 0-10 ustawia użytkownik.
4. Atrybut stały w wyborze dostaje 0,5 (nie różnicuje aut).

### Piktogram

- Każde auto to rząd ikon samochodu; jedna ikona = ustalona jednostka atrybutu: 25 KM, 1 l/100 km, 100 l, 25 000 PLN, 1 s.
- Liczba ikon zaokrąglona do całości (najwyżej 200); dokładna wartość wypisana obok nazwy.

## 5. Wyniki

### Miary rozkładu (95 aut)

| Miara | Moc [KM] | Spalanie [l/100 km] | Bagażnik [l] | Cena [PLN] | Przysp. [s] |
| --- | --- | --- | --- | --- | --- |
| Średnia | 297,60 | 8,74 | 426,24 | 874 812,68 | 7,28 |
| Mediana | 240,00 | 7,60 | 440,00 | 160 432,00 | 7,00 |
| Dominanta | 181,00 | 6,50; 6,70 | 0,00 | 66 989; 155 550; 187 341 | 7,50 |
| Minimum | 76,00 | 4,10 | 0,00 | 39 739,00 | 2,40 |
| Maksimum | 1 600,00 | 22,50 | 1 200,00 | 37 468 200,00 | 14,50 |
| Rozstęp | 1 524,00 | 18,40 | 1 200,00 | 37 428 461,00 | 12,10 |
| Q1 | 151,00 | 6,50 | 259,50 | 96 736,00 | 5,25 |
| Q3 | 363,00 | 10,65 | 532,50 | 313 938,50 | 9,00 |
| IQR | 212,00 | 4,15 | 273,00 | 217 202,50 | 3,75 |
| Wariancja | 61 406,56 | 12,34 | 67 366,23 | 17 030 338 854 794,01 | 8,28 |
| Odch. standardowe | 247,80 | 3,51 | 259,55 | 4 126 783,11 | 2,88 |
| Wsp. zmienności [%] | 83,27 | 40,18 | 60,89 | 471,73 | 39,52 |
| Skośność | 3,23 | 1,72 | 0,70 | 8,01 | 0,51 |
| Kurtoza nadmiarowa | 14,21 | 3,91 | 0,82 | 68,53 | -0,28 |

### Wnioski z miar rozkładu

- **Cena ma skrajnie prawostronnie skośny rozkład** (skośność 8,01, kurtoza 68,53). Średnia (875 tys. PLN) jest ponad 5 razy wyższa od mediany (160 tys. PLN), bo kilka supersamochodów ciągnie ją w górę. Typową cenę lepiej opisują mediana i IQR. Bez 11 odstających cen średnia spada do ok. 185 tys. PLN, a skośność do 1,29.
- **Wariancja ceny jest ogromna (ok. 1,7 * 10^13 PLN^2)**, bo wariancja ma jednostkę do kwadratu, a odchylenia supersamochodów od średniej są podnoszone do kwadratu. Do interpretacji służą odchylenie standardowe i współczynnik zmienności.
- **Moc** też jest prawostronnie skośna (3,23) z wysoką kurtozą (14,21) z tego samego powodu (Bugatti, McLaren).
- **Bagażnik i przyspieszenie mają rozkłady zbliżone do symetrycznych** (skośność 0,70 i 0,51), a przyspieszenie jest nieco bardziej spłaszczone od normalnego (kurtoza -0,28).
- **Największe zróżnicowanie względne ma cena** (CV 472%), najmniejsze spalanie i przyspieszenie (ok. 40%).

### Korelacje

Pearson:

| | Moc | Spalanie | Bagażnik | Cena | Przysp. |
| --- | --- | --- | --- | --- | --- |
| Moc | 1,000 | 0,742 | -0,232 | 0,765 | -0,672 |
| Spalanie | 0,742 | 1,000 | -0,114 | 0,561 | -0,467 |
| Bagażnik | -0,232 | -0,114 | 1,000 | -0,244 | 0,119 |
| Cena | 0,765 | 0,561 | -0,244 | 1,000 | -0,293 |
| Przysp. | -0,672 | -0,467 | 0,119 | -0,293 | 1,000 |

Spearman:

| | Moc | Spalanie | Bagażnik | Cena | Przysp. |
| --- | --- | --- | --- | --- | --- |
| Moc | 1,000 | 0,672 | -0,034 | 0,930 | -0,852 |
| Spalanie | 0,672 | 1,000 | 0,016 | 0,622 | -0,460 |
| Bagażnik | -0,034 | 0,016 | 1,000 | -0,040 | 0,142 |
| Cena | 0,930 | 0,622 | -0,040 | 1,000 | -0,845 |
| Przysp. | -0,852 | -0,460 | 0,142 | -0,845 | 1,000 |

### Wnioski z korelacji

- **Najsilniejsza zależność: moc i cena** (Pearson 0,765, Spearman 0,930). Mocniejsze auta są droższe.
- **Moc i przyspieszenie**: silna ujemna zależność (Spearman -0,852). Większa moc oznacza krótszy czas 0-100 km/h, co jest zgodne z intuicją fizyczną.
- **Moc i spalanie**: silna dodatnia (Pearson 0,742).
- **Bagażnik praktycznie nie zależy od pozostałych atrybutów** (Spearman od -0,04 do 0,14).
- **Pearson a Spearman**: przy cenie różnią się mocno (np. cena i przyspieszenie: -0,293 vs -0,845). Pearson jest wrażliwy na wartości skrajne (Bugatti), a Spearman działa na rangach, więc lepiej opisuje ten zbiór. Bez 11 odstających cen Pearson dla mocy i ceny rośnie z 0,765 do 0,844.
- Korelacja nie oznacza przyczynowości; zbiór to dobór modeli z jednego rynku.

### Ranking (przykład)

Przy równych wagach wszystkich atrybutów najwyżej wypadają: Geely Lynk & Co 08 EM-P (79,7), Toyota RAV4 Hybrid (71,5), Toyota Land Cruiser (68,0). Lynk & Co zawdzięcza wynik bardzo niskiemu spalaniu katalogowemu hybrydy plug-in (patrz "Jakość danych").

## 6. Otwarte kwestie

- **Zamiana prędkości maksymalnej na przyspieszenie** do potwierdzenia u prowadzącego.
- **Dominanta przy danych ciągłych**: obecnie z pojedynczych wartości (remisy, np. 3 dominanty ceny po 2 wystąpienia). Alternatywa: dominanta z szeregu rozdzielczego przedziałowego wzorem interpolacyjnym; nie wdrożona.
- **Koncentracja**: obecnie kurtoza; ewentualnie dodać współczynnik Giniego i krzywą Lorenza.
- **Bagażniki 0 l i podejrzanie małe**: zostawione jak w źródle; do decyzji, czy wykluczać je z analizy bagażnika.
- **Testy automatyczne** zostały tymczasowo usunięte; przed oddaniem warto je przywrócić.
- Do dokumentacji przydadzą się zrzuty ekranu każdej zakładki.
