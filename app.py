from datetime import date
from urllib.parse import urlparse
import html
import math

import plotly.express as px
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from analysis import ATTRS, describe, correlations, rank_cars
from db import initialize, read_cars, seed_demo, add_car

st.set_page_config(page_title="Car Metrics", page_icon="🚘", layout="wide")
st.caption("CAR METRICS / LABORATORIUM DANYCH")
st.title("Poznaj samochody przez liczby.")
st.write("Porównuj parametry, odkrywaj zależności i znajdź model pasujący do Twoich priorytetów.")
try:
    initialize()
    data = read_cars()
except SQLAlchemyError:
    st.error("Nie można połączyć się z PostgreSQL. Uruchom bazę i sprawdź konfigurację połączenia.")
    st.code("docker compose up --build")
    st.stop()

with st.sidebar:
    st.header("Baza samochodów")
    if st.button("Dodaj 30 rekordów demonstracyjnych"):
        try:
            seed_demo()
            st.rerun()
        except SQLAlchemyError:
            st.error("Nie udało się zapisać danych demonstracyjnych.")
    st.caption("Dane demonstracyjne są fikcyjne. Ponowne dodanie nie tworzy duplikatów.")
    with st.expander("Dodaj rzeczywisty samochód"):
        with st.form("add"):
            brand = st.text_input("Marka", max_chars=80)
            model = st.text_input("Model", max_chars=100)
            variant = st.text_input("Wersja silnika / wyposażenia", max_chars=100)
            year = st.number_input("Rocznik", 1900, 2100, 2024)
            values = {}
            for key, label in ATTRS.items():
                values[key] = st.number_input(label, min_value=0.0 if key == "trunk" else 0.1, value=1.0, step=0.1)
            source = st.text_input("URL specyfikacji i ceny", max_chars=1000)
            source_date = st.date_input("Data odczytu źródła", value=date.today(), max_value=date.today())
            submitted = st.form_submit_button("Zapisz do PostgreSQL")
        if submitted:
            if not all(v.strip() for v in (brand, model, variant)) or urlparse(source).scheme not in ("http", "https") or not urlparse(source).netloc:
                st.error("Uzupełnij markę, model, wersję i poprawny adres HTTP/HTTPS źródła.")
            else:
                try:
                    add_car(dict(brand=brand.strip(), model=model.strip(), variant=variant.strip(), year=int(year), **values, source_url=source.strip(), source_date=source_date, is_demo=False))
                    st.rerun()
                except IntegrityError:
                    st.error("Ten model, rocznik i wersja już istnieją albo dane naruszają ograniczenia bazy.")
                except SQLAlchemyError:
                    st.error("Nie udało się zapisać rekordu. Sprawdź połączenie z bazą.")

if data.empty:
    st.info("Baza jest pusta. Dodaj samochód lub załaduj 30 rekordów demonstracyjnych z panelu bocznego.")
    st.stop()

with st.sidebar:
    st.header("Filtry")
    kind = st.radio("Rodzaj danych", ["Demonstracyjne", "Rzeczywiste"], index=0 if data.is_demo.any() else 1)
    data = data[data.is_demo == (kind == "Demonstracyjne")].copy()
    brands = st.multiselect("Marki (puste = wszystkie)", sorted(data.brand.unique()))
    if brands:
        data = data[data.brand.isin(brands)]
    budget = st.number_input("Maksymalna cena [PLN]", min_value=0.0, value=float(data.price.max()) if not data.empty else 300000.0, step=10000.0)
    data = data[data.price <= budget].copy()

if data.empty:
    st.info("Brak samochodów dla wybranych filtrów. Zmień filtry lub dodaj dane.")
    st.stop()
if kind == "Demonstracyjne":
    st.warning("Tryb demonstracyjny: 30 fikcyjnych samochodów. Wyniki nie opisują rynku motoryzacyjnego.")
if len(data) < 30:
    st.info(f"Analizujesz {len(data)} obiektów. Projekt wymaga co najmniej 30 obiektów w zbiorze docelowym.")
data["Samochód"] = data.brand + " / " + data.model + " / " + data.variant + " / " + data.year.astype(str)
cols = st.columns(4)
for col, label, value in zip(cols, ["Samochody", "Średnia moc", "Średnie spalanie", "Mediana ceny"], [str(len(data)), f"{data.power.mean():.0f} KM", f"{data.fuel.mean():.1f} l/100 km", f"{data.price.median():,.0f} PLN"]):
    col.metric(label, value)

table, stats, charts, corr, ranking = st.tabs(["01 · Samochody", "02 · Statystyki", "03 · Porównania", "04 · Korelacje", "05 · Twój ranking"])
with table:
    st.subheader("Jeden wiersz. Jedna konkretna wersja.")
    st.dataframe(data[["Samochód", *ATTRS, "source_url", "source_date"]].rename(columns=ATTRS), hide_index=True, use_container_width=True)
with stats:
    st.subheader("Rozkład pięciu parametrów")
    st.dataframe(describe(data), use_container_width=True)
    st.caption("Wariancja i odchylenie: próba (n−1). Skośność: korekta obciążenia, minimum 3 obserwacje. Kurtoza nadmiarowa: minimum 4, rozkład normalny = 0. NaN oznacza miarę nieokreśloną. Przy braku powtórzeń dominanta = brak.")
    key = st.selectbox("Parametr rozkładu", list(ATTRS), format_func=ATTRS.get)
    st.plotly_chart(px.histogram(data, x=key, marginal="box", labels=ATTRS, color_discrete_sequence=["#22c5a0"]), use_container_width=True)
with charts:
    left, right = st.columns(2)
    x = left.selectbox("Oś X", list(ATTRS), index=3, format_func=ATTRS.get)
    y = right.selectbox("Oś Y", list(ATTRS), format_func=ATTRS.get)
    st.plotly_chart(px.scatter(data, x=x, y=y, color="brand", hover_name="Samochód", labels=ATTRS), use_container_width=True)
    st.subheader("Garaż obrazkowy")
    st.caption("Pełny samochód = jedna jednostka legendy; ostatnia ikona jest przycięta proporcjonalnie. Dokładna wartość widoczna przy nazwie.")
    metric = st.selectbox("Co porównujesz?", list(ATTRS), format_func=ATTRS.get)
    selected = st.multiselect("Wybierz do 6 samochodów", data["Samochód"].tolist(), default=data["Samochód"].head(4).tolist(), max_selections=6)
    unit = {"power": 25, "fuel": 1, "trunk": 100, "price": 25000, "speed": 25}[metric]
    st.write(f"🚘 = {unit:g} {ATTRS[metric].split('[')[1].rstrip(']')}")
    for _, row in data[data["Samochód"].isin(selected)].iterrows():
        count = row[metric] / unit
        # Fixed-width slots keep icon area proportional; scroll large values.
        icons = "".join(f'<span style="display:inline-block;width:{min(1, count-i)*32:.2f}px;overflow:hidden;flex-shrink:0"><span style="display:block;width:32px;font-size:24px">🚘</span></span>' for i in range(math.ceil(min(count, 200)) ))
        st.markdown(f'<div style="padding:12px 0"><b>{html.escape(row["Samochód"])}</b> · {row[metric]:g}<div style="display:flex;overflow-x:auto">{icons}</div></div>', unsafe_allow_html=True)
        if count > 200:
            st.caption("Wizualizacja ograniczona do 200 ikon; pełna wartość powyżej.")
with corr:
    method = st.radio("Współczynnik", ["pearson", "spearman"], horizontal=True)
    matrix = correlations(data, method)
    st.plotly_chart(px.imshow(matrix, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="RdBu", aspect="auto"), use_container_width=True)
    st.dataframe(matrix, use_container_width=True)
    st.caption("Pearson mierzy zależność liniową, Spearman monotoniczną. Korelacja nie oznacza przyczynowości. Minimum 3 obserwacje; stały atrybut daje wynik nieokreślony.")
    pairs = [(a, b, matrix.loc[a, b]) for i, a in enumerate(matrix.columns) for b in matrix.columns[i+1:] if matrix.loc[a, b] == matrix.loc[a, b]]
    st.subheader("Wnioski z aktualnego wyboru")
    if pairs:
        a, b, r = max(pairs, key=lambda item: abs(item[2]))
        st.write(f"Największa bezwzględna korelacja: **{a} ↔ {b}**, r = **{r:.3f}** (n = {len(data)}).")
    else:
        st.info("Za mało zmiennych obserwacji do wyznaczenia korelacji.")
    cheapest = data.loc[data.price.idxmin()]
    st.write(f"Najniższa cena: **{cheapest['Samochód']}** — {cheapest.price:,.0f} PLN. Rozstęp cen w wyborze: {data.price.max() - data.price.min():,.0f} PLN.")
    st.caption("Wnioski dotyczą wyłącznie wybranej próby i filtrów. Dobór modeli oraz wersji wpływa na wyniki.")
with ranking:
    st.subheader("Co ma dla Ciebie znaczenie?")
    st.write("Ustaw wagi. Niższa cena i spalanie zwiększają wynik; większa moc, bagażnik i prędkość również.")
    weights = {key: col.slider(label, 0, 10, 5) for col, (key, label) in zip(st.columns(5), ATTRS.items())}
    if sum(weights.values()):
        ranked = rank_cars(data, weights)
        st.dataframe(ranked[["Samochód", "wynik", *ATTRS]].rename(columns={**ATTRS, "wynik": "Wynik / 100"}), hide_index=True, use_container_width=True)
    else:
        st.info("Ustaw przynajmniej jedną wagę większą od zera.")
    st.caption("Ranking: ważona średnia po normalizacji min–max w aktualnym wyborze. Stały atrybut otrzymuje 0,5. Zmiana filtrów może zmienić kolejność.")
