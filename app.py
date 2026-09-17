import streamlit as st
import pandas as pd
import requests
import datetime

# 頁面基本設定
st.set_page_config(page_title="台股全類群金流與個股 Top10 排行", layout="wide", page_icon="📈")

st.title("📊 台股全類群金流與個股 Top 10 排行榜")
st.caption(f"資料更新時間：{datetime.date.today().strftime('%Y-%m-%d')}")

# 設定快取 1 小時 (3600 秒)
@st.cache_data(ttl=3600)
def fetch_twse_full_data():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        
        # 1. 抓取證交所全類股金流 API
        url_bfiamu = "https://openapi.twse.com.tw/v1/exchangeReport/BFIAMU"
        res_sector = requests.get(url_bfiamu, headers=headers, timeout=10)
        
        # 2. 抓取上市公司產業別資料
        url_company = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"
        res_company = requests.get(url_company, headers=headers, timeout=10)
        
        # 3. 抓取每日個股成交金額數據
        url_stocks = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
        res_stocks = requests.get(url_stocks, headers=headers, timeout=10)
        
        if res_sector.status_code == 200 and res_stocks.status_code == 200:
            # 整理全類股數據
            sector_df = pd.DataFrame(res_sector.json())
            sector_df = sector_df.rename(columns={
                "Industry": "類股名稱",
                "TradeValue": "成交金額",
                "Percentage": "今日金流比(%)"
            })
            sector_df["成交金額(億)"] = (pd.to_numeric(sector_df["成交金額"], errors='coerce') / 100000000).round(2)
            sector_df["今日金流比(%)"] = pd.to_numeric(sector_df["今日金流比(%)"], errors='coerce').round(2)
            
            # 整理個股與產業數據
            stocks_df = pd.DataFrame(res_stocks.json())
            if res_company.status_code == 200:
                comp_df = pd.DataFrame(res_company.json())[["公司代號", "產業別"]]
                stocks_df = pd.merge(stocks_df, comp_df, left_on="Code", right_on="公司代號", how="left")
            else:
                stocks_df["產業別"] = "其他"
                
            stocks_df["成交金額(億)"] = (pd.to_numeric(stocks_df["TradeValue"], errors='coerce') / 100000000).round(2)
            stocks_df["ClosingPrice"] = pd.to_numeric(stocks_df["ClosingPrice"], errors='coerce')
            stocks_df["Change"] = pd.to_numeric(stocks_df["Change"], errors='coerce')
            
            stocks_df = stocks_df.rename(columns={
                "Code": "股票代號",
                "Name": "股票名稱",
                "產業別": "類股名稱",
                "ClosingPrice": "收盤價",
                "Change": "漲跌"
            })
            
            return sector_df[["類股名稱", "成交金額(億)", "今日金流比(%)"]], stocks_df[["股票代號", "股票名稱", "類股名稱", "收盤價", "漲跌", "成交金額(億)"]]
        else:
            raise Exception("API 讀取異常")
            
    except Exception as e:
        # 容錯備援資料 (盤後 API 維護時自動切換)
        st.warning("⚠️ 目前讀取即時 API 受限（可能為非交易時間或 API 維護中），已載入備用數據。")
        
        fallback_sectors = pd.DataFrame({
            "類股名稱": ["半導體業", "電腦及週邊設備業", "電子零組件業", "航運業", "金融保險業", "電機機械業", "光電業", "通信網路業", "生技醫療業", "鋼鐵工業"],
            "成交金額(億)": [980.5, 420.3, 310.8, 220.0, 180.5, 150.2, 130.0, 110.4, 85.0, 60.2],
            "今日金流比(%)": [36.5, 15.6, 11.5, 8.2, 6.7, 5.6, 4.8, 4.1, 3.2, 2.2]
        })
        
        fallback_stocks = pd.DataFrame([
            {"股票代號": "2330", "股票名稱": "台積電", "類股名稱": "半導體業", "收盤價": 980.0, "漲跌": 15.0, "成交金額(億)": 350.2},
            {"股票代號": "2454", "股票名稱": "聯發科", "類股名稱": "半導體業", "收盤價": 1380.0, "漲跌": 20.0, "成交金額(億)": 120.5},
            {"股票代號": "2303", "股票名稱": "聯電", "類股名稱": "半導體業", "收盤價": 54.5, "漲跌": 0.5, "成交金額(億)": 85.3},
            {"股票代號": "3034", "股票名稱": "聯詠", "類股名稱": "半導體業", "收盤價": 610.0, "漲跌": -5.0, "成交金額(億)": 60.1},
            {"股票代號": "3711", "股票名稱": "日月光投控", "類股名稱": "半導體業", "收盤價": 162.0, "漲跌": 2.0, "成交金額(億)": 55.4},
            {"股票代號": "2317", "股票名稱": "鴻海", "類股名稱": "電腦及週邊設備業", "收盤價": 200.0, "漲跌": 4.0, "成交金額(億)": 210.8},
            {"股票代號": "2382", "股票名稱": "廣達", "類股名稱": "電腦及週邊設備業", "收盤價": 290.0, "漲跌": 6.0, "成交金額(億)": 130.5},
            {"股票代號": "3231", "股票名稱": "緯創", "類股名稱": "電腦及週邊設備業", "收盤價": 108.0, "漲跌": -1.0, "成交金額(億)": 65.2},
            {"股票代號": "2603", "股票名稱": "長榮", "類股名稱": "航運業", "收盤價": 185.0, "漲跌": 3.0, "成交金額(億)": 110.4},
            {"股票代號": "2609", "股票名稱": "陽明", "類股名稱": "航運業", "收盤價": 62.5, "漲跌": 1.2, "成交金額(億)": 60.8},
        ])
        return fallback_sectors, fallback_stocks

# 載入數據
sector_df, stocks_df = fetch_twse_full_data()

# 1. 頂部看板 (前三名金流大戶類股)
sector_sorted = sector_df.sort_values(by="今日金流比(%)", ascending=False).reset_index(drop=True)

c1, c2, c3 = st.columns(3)
if len(sector_sorted) >= 3:
    c1.metric("🥇 第一金流大戶", sector_sorted.iloc[0]["類股名稱"], f"{sector_sorted.iloc[0]['今日金流比(%)']}% ({sector_sorted.iloc[0]['成交金額(億)']}億)")
    c2.metric("🥈 第二金流大戶", sector_sorted.iloc[1]["類股名稱"], f"{sector_sorted.iloc[1]['今日金流比(%)']}% ({sector_sorted.iloc[1]['成交金額(億)']}億)")
    c3.metric("🥉 第三金流大戶", sector_sorted.iloc[2]["類股名稱"], f"{sector_sorted.iloc[2]['今日金流比(%)']}% ({sector_sorted.iloc[2]['成交金額(億)']}億)")

st.markdown("---")

# 2. 全類群金流排行榜
st.subheader("🏆 全類群金流排行榜 (由高至低)")
st.dataframe(
    sector_sorted,
    use_container_width=True,
    height=400
)

st.markdown("---")

# 3. 類群 Top 10 個股排行榜查詢
st.subheader("🔍 類群個股金流 Top 10 排行")

selected_sector = st.selectbox(
    "請選擇要查看的類群：",
    options=sector_sorted["類股名稱"].tolist()
)

if not stocks_df.empty:
    sub_stocks = stocks_df[stocks_df["類股名稱"] == selected_sector]
    if sub_stocks.empty:
        # 模糊匹配備用
        clean_name = selected_sector.replace("業", "").replace("工業", "")
        sub_stocks = stocks_df[stocks_df["類股名稱"].str.contains(clean_name, na=False)]
    
    top10_stocks = sub_stocks.sort_values(by="成交金額(億)", ascending=False).head(10).reset_index(drop=True)
    
    if not top10_stocks.empty:
        st.write(f"📊 **【{selected_sector}】成交金額前 10 大個股排行榜：**")
        st.dataframe(top10_stocks[["股票代號", "股票名稱", "成交金額(億)", "收盤價", "漲跌"]], use_container_width=True)
    else:
        st.info(f"尚無 【{selected_sector}】 的個股細部成交資料。")
