import streamlit as st
import pandas as pd
from datetime import datetime
from metrics.aggregations import load_aggregations
from jobs.ingest_job import run_ingest


st.set_page_config(page_title="Ministry Data Visualizer", layout="wide")


def main() -> None:
    st.title("同工分析 App")
    st.caption("数据源：Google Sheet 总表 A,Q,R,S,T,U | 后端：DuckDB")

    with st.sidebar:
        st.header("控制台")
        if st.button("手动刷新（读取 Google Sheet）"):
            with st.spinner("正在刷新数据..."):
                run_ingest()
            st.success("刷新完成")

        granularity = st.selectbox("时间颗粒度", ["year", "quarter", "month"], index=2)

    agg = load_aggregations(granularity=granularity)
    if agg is None or agg.empty:
        st.info("暂无数据，请先点击左侧手动刷新。")
        return

    st.subheader("总体趋势")
    st.line_chart(agg.set_index("period")["service_count"])

    st.subheader("同工参与情况")
    st.dataframe(agg)


if __name__ == "__main__":
    main()


