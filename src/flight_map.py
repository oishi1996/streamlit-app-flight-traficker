import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium

# APIキー
API_KEY = "3e526ce1a7cba6dc6b669f5d25dc5779"
API_URL = f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}"

def fetch_flight_data():
    """aviationstack APIからフライトデータを取得"""
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        return data.get("data", [])
    else:
        st.error("APIからデータを取得できませんでした。")
        return []

def process_flight_data(flights):
    """フライトデータを表形式に整形"""
    processed_data = []
    for flight in flights:
        processed_data.append({
            "日付": flight.get("flight_date", "不明"),
            "ステータス": flight.get("flight_status", "不明"),
            "航空会社": flight["airline"]["name"] if flight.get("airline") else "不明",
            "便名": flight["flight"]["iata"] if flight.get("flight") else "不明",
            "出発地": flight["departure"]["airport"] if flight.get("departure") else "不明",
            "出発IATA": flight["departure"]["iata"] if flight.get("departure") else "不明",
            "出発予定時刻": flight["departure"]["scheduled"] if flight.get("departure") else "不明",
            "到着地": flight["arrival"]["airport"] if flight.get("arrival") else "不明",
            "到着IATA": flight["arrival"]["iata"] if flight.get("arrival") else "不明",
            "到着予定時刻": flight["arrival"]["scheduled"] if flight.get("arrival") else "不明",
            "遅延 (分)": flight["departure"]["delay"] if flight.get("departure") and flight["departure"].get("delay") else 0,
            "実際の高度 (m)": flight["live"]["altitude"] if flight.get("live") else "なし"
        })
    return pd.DataFrame(processed_data)

def display_flight_map(flights):
    """飛行中のフライトをマップに表示"""
    m = folium.Map(location=[20, 0], zoom_start=2)
    for flight in flights:
        # Show all flights regardless of altitude
        latitude = flight["live"]["latitude"] if flight.get("live") and flight["live"].get("latitude") else 0
        longitude = flight["live"]["longitude"] if flight.get("live") and flight["live"].get("longitude") else 0
        callsign = flight["flight"]["iata"] if flight.get("flight") else "不明"
        altitude = flight["live"]["altitude"] if flight.get("live") else "なし"
        folium.Marker(
            location=[latitude, longitude],
            popup=f"Flight: {callsign}\nAltitude: {altitude} m",
            icon=folium.Icon(color="red", icon="plane", prefix="fa"),
        ).add_to(m)
    return m

def main():
    st.title("リアルタイム飛行機情報")
    
    # APIからデータ取得
    flights = fetch_flight_data()
    df = process_flight_data(flights)
    
    # 表として表示
    st.write("📋 フライト一覧")
    st.dataframe(df)

    # マップに飛行中のフライトを表示
    st.write("✈️ 飛行中のフライトマップ")
    flight_map = display_flight_map(flights)
    st_folium(flight_map, width=700, height=500)

if __name__ == "__main__":
    main()
