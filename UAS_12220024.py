import streamlit as st
import plotly_express as px
import pandas as pd


df1 = pd.read_csv("produksi_minyak_mentah.csv")
df2 = pd.read_json("kode_negara_lengkap.json")

# sidebar
st.sidebar.title("Menu")
menu_select = [
    'Home',
    'Data produksi negara',
    'Negara dengan produksi tertinggi pada tahun tertentu',
    'Negara dengan produksi tertinggi',
    'Ringkasan produksi pada tahun tertentu dan keseluruhan tahun'
]
selected_menu = st.sidebar.radio('', menu_select)

df_joined = df1.merge(df2, how="left",
                      left_on="kode_negara", right_on="alpha-3")


# Home
if selected_menu == 'Home':
    st.title('UAS Pemrograman Komputer - Teknik Perminyakan 2020')
    st.subheader('Rafli Fawwaz - 12220024')
    st.write('Aplikasi GUI berbasis Streamlit untuk menampilkan informasi produksi minyak mentah'\
            ' pada negara-negara di seluruh dunia')

# Pengerjaan untuk poin A
elif selected_menu == 'Data produksi negara':
    st.title(selected_menu.capitalize())
    countries_code = pd.Series(df1['kode_negara'].unique()).sort_values()

    country_choice = st.selectbox(
        "Pilih negara dari list dropdown di bawah ini", pd.Series(df_joined['name'].unique()).sort_values())
    st.write(f"Negara terpilih: {country_choice}")

    filtered = df_joined[df_joined['name'] == country_choice]
    st.write(px.line(filtered, x="tahun", y="produksi",
                     title=f"Grafik Produksi Minyak Mentah untuk Negara {country_choice}"))


# Pengerjaan untuk Poin B
elif selected_menu == 'Negara dengan produksi tertinggi pada tahun tertentu':
    st.title(selected_menu.capitalize())
    year_list = df1['tahun'].unique()
    year_list.sort()
    year_choice = st.selectbox("Pilih Tahun", year_list[::-1])
    n_largest = df_joined[df_joined['tahun'] == year_choice].groupby(
        'name').sum().sort_values('produksi', ascending=False)['produksi']
    n = st.slider('Jumlah negara yang ditampilkan', 2, 25)

    fig = px.bar(n_largest.iloc[:n], labels={
        'name': 'Nama Negara', 'value': 'Produksi dalam 1 Tahun'},
        title=f'Jumlah Produksi pada Tahun {year_choice}')
    fig.update_layout(showlegend=False)
    fig.update_traces(width=0.5)
    st.write(fig)

# Pengerjaan untuk poin C
elif selected_menu == 'Negara dengan produksi tertinggi':
    st.title(selected_menu)

    # Melakukan grouping pada dataframe untuk mendapatkan total produksi negara
    df_cumulative = df_joined.groupby('name').sum()
    # Melakukan sorting pada nilai produksi agar ditampilkan dari yang terbesar
    df_cumulative = df_cumulative.sort_values(
        'produksi', ascending=False)['produksi']

    st.subheader('Menampilkan jumlah produksi terbesar secara kumulatif')
    n = st.slider('Jumlah negara yang ditampilkan', 2, 25)

    # Membuat grafik dengan plotly
    fig = px.bar(df_cumulative.iloc[:n], labels={
        'name': 'Nama Negara', 'value': 'Total Produksi'},
        title='Produksi Kumulatif')
    fig.update_layout(showlegend=False)
    fig.update_traces(width=0.5)
    st.write(fig)


# Pengerjaan untuk poin D
elif selected_menu == 'Ringkasan produksi pada tahun tertentu dan keseluruhan tahun':
    # Prosedur untuk menampilkan informasi suatu negara
    def show_info(country_name, year):
        df_country = df_joined[df_joined['name'] == country_name]
        alpha3_code = df_country["alpha-3"].iloc[0]
        alpha2_code = df_country["alpha-2"].iloc[0]
        region = df_country["region"].iloc[0]
        sub_region = df_country["sub-region"].iloc[0]
        production_year = df_country[(df_country["name"] == country_name) & (
            df_country["tahun"] == year)]["produksi"]
        total_prod = df_country[(df_country["name"] ==
                                 country_name)]["produksi"].sum()

        # Tampilkan hasilnya pada streamlit
        st.write(f'Nama Negara: {country_name}')
        st.write(f'Kode Negara: {alpha3_code}/{alpha2_code}')
        st.write(f'Region: {region}')
        st.write(f'Sub-Region: {sub_region}')
        if year is None:
            st.write(f'Total produksi: {round(total_prod, 2)}')
        else:
            st.write(
                f'Produksi pada tahun {year}: {round(production_year.iloc[0], 2)}')
            pass

    st.title(selected_menu)

    # Pilih untuk tampilkan tahun tertentu atau keseluruhan tahun
    choice = st.radio(
        "", ["Ringkasan untuk tahun tertentu", "Ringkasan keseluruhan tahun"])

    if choice == "Ringkasan untuk tahun tertentu":
        year_list = df1['tahun'].unique()
        year_list.sort()
        year_choice = st.selectbox("Pilih Tahun", year_list[::-1])

        # Sort dataframe berdasarkan total produksi
        sorted_df = df_joined[df_joined['tahun'] == year_choice].groupby(
            'name').sum().sort_values('produksi', ascending=False)
        country_max = sorted_df.index[0]
        country_min = sorted_df[sorted_df['produksi'] > 0].index[-1]
        country_zero = sorted_df[sorted_df['produksi'] == 0]
    else:
        # keseluruhan tahun
        sorted_df = df_joined.groupby('name').sum(
        ).sort_values('produksi', ascending=False)
        country_max = sorted_df.index[0]
        country_min = sorted_df[sorted_df['produksi'] > 0].index[-1]
        country_zero = sorted_df[sorted_df['produksi'] == 0]
        year_choice = None

    # Tampilkan data
    st.markdown('## Negara dengan Produksi Terbesar')
    show_info(country_max, year_choice)

    st.markdown('## Negara dengan Produksi Terkecil')
    show_info(country_min, year_choice)

    st.markdown('## Negara dengan Produksi Nol')
    for country in country_zero.index.sort_values():
        with st.expander(country):
            show_info(country, year_choice)
