# app.py

import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
from queries import search_places, get_tokyo_stations
import subprocess
from datetime import datetime
import os


st.set_page_config(layout="wide")
st.title("東京ビジネス検索デモ")


# -----------------------------
# 駅リストをキャッシュする
# -----------------------------
@st.cache_data
def load_stations():
    stations_data = get_tokyo_stations()
    return {
        row.name: (row.lat, row.lon)
        for row in stations_data
    }


stations = load_stations()


# -----------------------------
# サイドバー
# -----------------------------
st.sidebar.header("検索設定")

search_term = st.sidebar.text_input("検索キーワード", "カフェ")

radius = st.sidebar.slider(
    "半径（メートル）",
    100,
    5000,
    500
)

station_name = st.sidebar.text_input("駅名（例：秋葉原）", "秋葉原")

if station_name in stations:
    lat, lon = stations[station_name]

# -----------------------------
# セッション状態
# -----------------------------
if "results" not in st.session_state:
    st.session_state.results = None

if "center" not in st.session_state:
    st.session_state.center = None


# -----------------------------
# 検索ボタン
# -----------------------------
if st.sidebar.button("検索"):

    lat, lon = stations[station_name]

    results = search_places(
        search_term=search_term,
        lat=lat,
        lon=lon,
        radius=radius
    )

    st.session_state.results = results
    st.session_state.center = (lat, lon)


results = st.session_state.results

# -----------------------------
# データ更新ボタン
# -----------------------------
st.sidebar.markdown("## 🔄 データ管理")

# 最終更新日時を表示
if os.path.exists("last_update.txt"):
    with open("last_update.txt", "r") as f:
        last_update = f.read()
else:
    last_update = "未更新"

st.sidebar.write(f"最終更新日時: {last_update}")

# 更新ボタン
if st.sidebar.button("データ更新"):
    st.write("DEBUG: データを更新中... 数分かかる場合があります。")
    with st.spinner("データ更新中です... お待ちください ⏳"):
        try:
            st.write("DEBUG: プロセスを実行中...")

            # Step 1: OSMデータ更新
            subprocess.run([
                "docker", "exec", "tokyo_osm_updater",
                "osm2pgsql-replication", "update",
                "-d", "tokyo_osm", "-H", "postgis", "-U", "postgres"
            ], check=True)

            # Step 2: テーブル更新
            st.write("DEBUG: ビジネステーブルを更新中...")
            subprocess.run(
                "docker exec -i tokyo_postgis psql -U postgres -d tokyo_osm < sql/refresh_business_table.sql",
                shell=True,
                check=True
            )

            # 更新時間を保存
            st.write("DEBUG: タイムスタンプを保存中...")
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("last_update.txt", "w") as f:
                f.write(now)

            st.success("✅ データ更新が完了しました！")

        except Exception as e:
            st.error(f"❌ 更新に失敗しました: {e}")


# -----------------------------
# 結果表示
# -----------------------------
if results:

    df = pd.DataFrame(results)

    df = df.rename(columns={
        "name": "名前",
        "amenity": "カテゴリ",
        "shop": "店舗種別",
        "address": "住所",
        "phone": "電話番号",
        "website": "ウェブサイト",
        "lat": "緯度",
        "lon": "経度"
    })


    # テーブル表示用に必要な列のみ選択
    table_df = df[[
        "名前",
        "住所",
        "電話番号",
        "ウェブサイト"
    ]]


    # -----------------------------
    # 地図表示
    # -----------------------------
    center_lat, center_lon = st.session_state.center

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=15
    )

    folium.Marker(
        [center_lat, center_lon],
        tooltip=station_name,
        icon=folium.Icon(color="red")
    ).add_to(m)


    for _, r in df.iterrows():

        folium.Marker(
            [r["緯度"], r["経度"]],
            tooltip=f"{r['名前']} ({r['カテゴリ'] or r['店舗種別']})"
        ).add_to(m)


    st.subheader("地図")

    st_folium(
        m,
        width=1200,
        height=600
    )


    # -----------------------------
    # テーブル表示
    # -----------------------------
    st.subheader("検索結果")

    st.dataframe(
        table_df,
        column_config={
            "ウェブサイト": st.column_config.LinkColumn("ウェブサイト")
        },
        use_container_width=True
    )


elif results is not None:

    st.warning("結果が見つかりませんでした。")