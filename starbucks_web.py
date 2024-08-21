import pandas as pd
import streamlit as st
from pymongo import MongoClient
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static

plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False

mongo_url = 'mongodb+srv://axz1420:dlgusdn113!@store.jvq4o15.mongodb.net/?retryWrites=true&w=majority&appName=store'
client = MongoClient(mongo_url)
db = client['starbucks']

store_collections = {
    '충북': db['choongbook_stores'],
    '대구': db['deagu_stores'],
    '대전': db['deajun_stores'],
    '광주': db['gwangju_stores'],
    '강원': db['gwangwon_stores'],
    '경북': db['gyungbook_stores'],
    '경기': db['gyunggi_stores'],
    '경남': db['gyungnam_stores'],
    '인천': db['incheon_stores'],
    '제주': db['jeju_stores'],
    '전북': db['junbook_stores'],
    '전남': db['junnam_stores'],
    '세종': db['sejung_stores'],
    '서울': db['seoul_stores'],
    '울산': db['ulsan_stores'],
}

stores = db['stores']

drink_menu = db['drink_menu']

#--------------------------------

logo_url = "https://www.starbucks.co.kr/common/img/common/logo.png"
st.markdown(f"<div style='text-align: center; margin-bottom: 60px;'><img src='{logo_url}' width='80'></div>", unsafe_allow_html=True)


col1, blank, col2 = st.columns([2, 0.5, 5])

#--------------------------------

with col1:
    # st.write("---")
    st.markdown("<h5 style='margin-bottom: -80px'; margin-top: -80px;>매장검색</h5>", unsafe_allow_html=True)
    st.write("---")
    all_area_button = st.button('전체지역 매장 표시')
    category = st.selectbox('지역선택', ['서울', '경기', '인천', '강원', '충북', '충남', '대전', '대구', '광주', '울산', '부산', '경북', '경남', '전북', '전남', '제주'])
    st.write("---")
    st.markdown("<h5 style='margin-bottom: -80px'; margin-top: -80px;>메뉴</h5>", unsafe_allow_html=True)
    st.write("---")
    drink_menu_button = st.button('전체 음료 메뉴')
    st.write('')
    st.write('')
    kcal_button = st.button('칼로리 순위')
    protein_button = st.button('단백질 순위')

#--------------------------------

def show_map(df):
    map = folium.Map(location=[df['위도'].mean(), df['경도'].mean()], zoom_start=12, width='460px', height='460px')
    for data in range(len(df)):
        popup = folium.Popup(f"<h5><strong>{df['매장명'][data] + '점'}</strong></h5>{df['주소'][data]}</br>{df['전화번호'][data]}",
                             max_width=200)
        folium.Marker([df['위도'][data], df['경도'][data]], popup=popup).add_to(map)

    return map

#--------------------------------


with col2:
    if drink_menu_button:
        category = None
        data = drink_menu.find()
        df = pd.DataFrame(data)
        df1 = df.drop(columns=['_id', 'img_url', 'a_prod'])
        df1.index = df.index + 1

        st.markdown("<h4 style='text-align: center; margin-bottom: -80px'>전체 음료 메뉴</h4>", unsafe_allow_html=True)
        st.write("---")
        st.dataframe(df1)

        st.write("---")
        st.markdown("<h6 style='text-align: center; margin-bottom: 20px'>전체 음료 메뉴</h6>", unsafe_allow_html=True)
        for index, row in df.iterrows():
            st.markdown(f"""
                        <div class='drink-card' style='text-align: center;'>
                            <div class='drink-image'>
                                <img src='{row['img_url']}' width='300' style='margin-bottom: 30px;'>
                            </div>
                            <div class='drink-details'>
                                <p><strong>이름 :</strong> {row['이름']}</p>
                                <p><strong>1회 제공량 (kcal) :</strong> {row['1회제공량(kcal)']}ml</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            st.write("---")

    elif all_area_button:
        data = stores.find()
        df = pd.DataFrame(data)
        df = df.drop(columns=['_id'])
        df = df[['매장명', '주소', '전화번호', '위도', '경도']]
        st.markdown("<h4 style='text-align: center; margin-bottom: -50px'>전체지역 매장</h4>", unsafe_allow_html=True)
        st.write("---")
        folium_static(show_map(df))
        df.index = df.index + 1
        st.dataframe(df)

    elif kcal_button:
        data = drink_menu.find()
        df = pd.DataFrame(data)
        df = df.drop(columns=['_id', 'img_url', 'a_prod'])
        df = df[['이름', '1회제공량(kcal)']]

        df['1회제공량(kcal)'] = pd.to_numeric(df['1회제공량(kcal)'])

        df = df.sort_values(by='1회제공량(kcal)', ascending=True).reset_index(drop=True)
        df.index = df.index + 1

        st.markdown("<h4 style='text-align: center; margin-bottom: -80px'>칼로리 순위</h4>", unsafe_allow_html=True)
        st.write("---")
        st.dataframe(df, width=500, height=500)

        df = df[df['1회제공량(kcal)'] > 0]
        df_top30 = df.head(30)

        fig, ax = plt.subplots(figsize=(20, 10))
        bars = ax.barh(df_top30['이름'], df_top30['1회제공량(kcal)'])
        ax.set_xlabel('1회 제공량 (kcal)')
        ax.set_ylabel('이름')
        ax.set_title('음료별 1회 제공량 (kcal) 순위 (상위 30개)')
        ax.invert_yaxis()

        # 막대 옆에 수치 표시
        for bar in bars:
            ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f'{bar.get_width():.0f}', va='center')

        st.pyplot(fig)

    elif protein_button:
        data = drink_menu.find()
        df = pd.DataFrame(data)
        df = df.drop(columns=['_id', 'img_url', 'a_prod'])
        df = df[['이름', '단백질(g)']]

        df['단백질(g)'] = pd.to_numeric(df['단백질(g)'])

        df = df.sort_values(by='단백질(g)', ascending=False).reset_index(drop=True)
        df.index = df.index + 1

        st.markdown("<h4 style='text-align: center; margin-bottom: -80px'>단백질 순위</h4>", unsafe_allow_html=True)
        st.write("---")
        st.dataframe(df, width=500, height=500)

        df = df[df['단백질(g)'] > 0]
        df_top30 = df.head(30)

        fig, ax = plt.subplots(figsize=(20, 10))
        bars = ax.barh(df_top30['이름'], df_top30['단백질(g)'])
        ax.set_xlabel('단백질 (g)')
        ax.set_ylabel('이름')
        ax.set_title('음료별 단백질 (g) 순위 (상위 30개)')
        ax.invert_yaxis()

        # 막대 옆에 수치 표시
        for bar in bars:
            ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f'{bar.get_width():.0f}', va='center')

        st.pyplot(fig)

    elif category:
        data = store_collections[category].find()
        df = pd.DataFrame(data)
        if not df.empty:
            df = df.drop(columns=['_id'])
            df = df[['매장명', '주소', '전화번호', '위도', '경도']]
            st.markdown(f"<h4 style='text-align: center; margin-bottom: -80px'>{category} 매장</h4>",
                            unsafe_allow_html=True)
            st.write("---")
            folium_static(show_map(df))

            df = df.drop(columns=['위도', '경도'])
            df.index = df.index + 1
            st.dataframe(df)




