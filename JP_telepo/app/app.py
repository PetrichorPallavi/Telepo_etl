import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
from queries import search_places, get_tokyo_stations
import subprocess
from datetime import datetime
import os

st.set_page_config(layout="wide")
st.title("🗺️ 東京ビジネス検索デモ")

# -------------------------
# PATH
# -------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TIME_FILE = os.path.join(BASE_DIR, "last_update.txt")

# -----------------------------
# 駅リスト
# -----------------------------
@st.cache_data
def load_stations():
    return get_tokyo_stations()

stations_data = load_stations()
stations = {row.name: (row.lat, row.lon) for row in stations_data}

# -----------------------------
# サイドバー
# -----------------------------
st.sidebar.header("🔍 検索設定")

search_term = st.sidebar.text_input("検索キーワード", "カフェ")
radius = st.sidebar.slider("半径（メートル）", 100, 5000, 500)
station_name = st.sidebar.text_input("駅名（例：秋葉原）", "秋葉原")

# -----------------------------
# セッション状態
# -----------------------------
if "results" not in st.session_state:
    st.session_state.results = None

if "center" not in st.session_state:
    st.session_state.center = None

# -----------------------------
# 検索
# -----------------------------
if st.sidebar.button("検索"):

    if station_name not in stations:
        st.error("駅が見つかりません")
    else:
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
# データ更新
# -----------------------------
st.sidebar.markdown("## 🔄 データ管理")

if os.path.exists("last_update.txt"):
    with open("last_update.txt", "r") as f:
        last_update = f.read()
else:
    last_update = "未更新"

st.sidebar.write(f"最終更新日時: {last_update}")

if st.sidebar.button("データ更新"):
    with st.spinner("更新中..."):
        try:
            subprocess.run([
                "docker", "exec", "tokyo_osm_updater",
                "osm2pgsql-replication", "update",
                "-d", "tokyo_osm", "-H", "postgis", "-U", "postgres"
            ], check=True)

            subprocess.run(
                "docker exec -i tokyo_postgis psql -U postgres -d tokyo_osm < sql/refresh_business_table.sql",
                shell=True,
                check=True
            )

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("last_update.txt", "w") as f:
                f.write(now)

            st.success("✅ 更新完了")

        except Exception as e:
            st.error(f"❌ 失敗: {e}")

# -----------------------------
# 結果表示
# -----------------------------
if results:

    # 🔥 IMPORTANT: ensure results is list of dicts or tuples
    df = pd.DataFrame(results)

    if df.empty:
        st.warning("結果が見つかりませんでした")
        st.stop()

    # -----------------------------
    # カラム安全対策
    # -----------------------------
    for col in ["phone", "website"]:
        if col not in df.columns:
            df[col] = None

    # -----------------------------
    # 電話リンク作成
    # -----------------------------
    df["phone_link"] = df["phone"].apply(
        lambda x: f"tel:{x}" if pd.notnull(x) and x != "" else None
    )

    # -----------------------------
    # リネーム
    # -----------------------------
    df = df.rename(columns={
        "name": "名前",
        "amenity": "カテゴリ",
        "shop": "店舗種別",
        "address": "住所",
        "phone": "電話番号",
        "phone_link": "電話リンク",
        "website": "ウェブサイト",
        "distance": "距離（m）",
        "lat": "緯度",
        "lon": "経度"
    })

    # -----------------------------
    # 地図
    # -----------------------------
    center_lat, center_lon = st.session_state.center

    m = folium.Map(location=[center_lat, center_lon], zoom_start=15)

    folium.Marker(
        [center_lat, center_lon],
        tooltip=station_name,
        icon=folium.Icon(color="red")
    ).add_to(m)

    for _, r in df.iterrows():
        folium.Marker(
            [r["緯度"], r["経度"]],
            tooltip=f"{r['名前']}"
        ).add_to(m)

    st.subheader("地図")
    st_folium(m, width=1200, height=600)

    # -----------------------------
    # テーブル
    # -----------------------------
    st.subheader("検索結果")

    columns_to_show = [
        "名前",
        "住所",
        "電話リンク",
        "ウェブサイト",
        "距離（m）"
    ]

    table_df = df[[c for c in columns_to_show if c in df.columns]]

    st.dataframe(
        table_df,
        column_config={
            "ウェブサイト": st.column_config.LinkColumn("ウェブサイト"),
            "電話リンク": st.column_config.LinkColumn("電話番号")
        },
        use_container_width=True
    )

elif results is not None:
    st.warning("結果が見つかりませんでした。")
