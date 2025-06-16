import pandas as pd
import streamlit as st

# 데이터 로드
df = pd.read_csv("all_reviews_with_category_full_corrected.csv", encoding="utf-8")


# Streamlit UI
st.title("👕 내 키워드로 옷 추천받기")

user_input = st.text_input("추천 받고 싶은 키워드를 입력하세요 (예: 바지, 여름, 슬랙스 등)").strip()
min_positive_ratio = st.slider("긍정 리뷰 비율(%) 최소 기준", 0, 100, 50)

# 계층적 카테고리 구조
category_map = {
    "상의": ["티셔츠", "셔츠", "블라우스", "반팔", "나시", "긴팔"],
    "하의": ["바지", "치마", "슬랙스", "청바지", "여름바지"],
}

if user_input:
    user_keywords = [kw.strip() for kw in user_input.split(",")]
    detected_items = []
    for keyword in user_keywords:
        if keyword in category_map:
            detected_items.extend(category_map[keyword])
        else:
            detected_items.append(keyword)

    filtered = df[df["category"].apply(lambda x: any(item in str(x) for item in detected_items))]

    if not filtered.empty:
        result = filtered.groupby("source_file").agg({
            "review": "count",
            "sentiment": lambda x: (x == "positive").mean() * 100,
            "image_path": "first",
            "product_url": "first"
        }).rename(columns={
            "review": "리뷰 수",
            "sentiment": "긍정 리뷰 비율 (%)",
            "image_path": "이미지",
            "product_url": "제품 링크"
        }).reset_index()

        result = result[result["긍정 리뷰 비율 (%)"] >= min_positive_ratio]
        result = result.sort_values(by="리뷰 수", ascending=False)

        for _, row in result.iterrows():
            st.markdown(f"### 📦 [{row['source_file']}]({row['제품 링크']})")
            st.image(row["이미지"], width=300)
            st.write(f"👍 리뷰 수: {row['리뷰 수']}, 긍정 비율: {row['긍정 리뷰 비율 (%)']:.1f}%")
            st.markdown("---")
    else:
        st.warning("❌ 해당 키워드에 맞는 제품이 없습니다.")
else:
    st.info("🔎 먼저 키워드를 입력해주세요.")
