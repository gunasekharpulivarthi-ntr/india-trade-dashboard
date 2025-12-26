#libraries importing

import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile

#tile define
st.title("India Trade Dashboard")

# 1.Load Zip 
with zipfile.ZipFile("archive.zip","r") as z:
    export_df = pd.read_csv(z.open("2010_2021_HS2_export.csv"))
    import_df = pd.read_csv(z.open("2010_2021_HS2_import.csv"))

export_df["TradeType"] = "Export"
import_df["TradeType"] = "Import"

df = pd.concat([export_df, import_df], ignore_index=True)

df = df.rename(columns={
    "value":"TradeValue",
    "country":"Country",
    "year":"Year"
})

# 2.Cleaning 
df = df.drop_duplicates()
df = df.dropna(subset=["TradeValue"])
df["Year"] = df["Year"].astype(int)
df["TradeValue"] = df["TradeValue"].astype(float)

# 3.Filters 
st.sidebar.header("Filters")

year = st.sidebar.multiselect("Select Year", sorted(df["Year"].unique()))
country = st.sidebar.multiselect("Select Country", sorted(df["Country"].unique()))

filtered = df.copy()

if year:
    filtered = filtered[filtered["Year"].isin(year)]

if country:
    filtered = filtered[filtered["Country"].isin(country)]

# 4.KPI Cards 
total_exports = filtered[filtered["TradeType"]=="Export"]["TradeValue"].sum()
total_imports = filtered[filtered["TradeType"]=="Import"]["TradeValue"].sum()
trade_balance = total_exports - total_imports

c1,c2,c3 = st.columns(3)
c1.metric("Total Exports", f"{total_exports:,.2f}")
c2.metric("Total Imports", f"{total_imports:,.2f}")
c3.metric("Trade Balance", f"{trade_balance:,.2f}")

# 5.Year Trend 
trend = filtered.groupby(["Year","TradeType"])["TradeValue"].sum().reset_index()

fig1 = px.line(trend, x="Year", y="TradeValue", color="TradeType",
               title="Year-wise Import vs Export Trend")

st.plotly_chart(fig1, width='stretch')

# 6.Top Countries 
top_countries = filtered.groupby(["Country","TradeType"])["TradeValue"].sum().reset_index()
top_countries = top_countries.sort_values("TradeValue",ascending=False).head(10)

fig2 = px.bar(top_countries, x="Country", y="TradeValue", color="TradeType",
              title="Top 10 Trading Countries")

st.plotly_chart(fig2, width='stretch')


# 7.Commodity Treemap 
fig3 = px.treemap(filtered, path=["TradeType","Commodity"], values="TradeValue",
                  title="Commodity-wise Trade Treemap")

st.plotly_chart(fig3, width='stretch')

