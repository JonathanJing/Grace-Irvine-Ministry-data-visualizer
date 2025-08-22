import streamlit as st
import pandas as pd
from metrics.aggregations import (
    load_aggregations,
    load_participants_table,
    list_volunteers,
    volunteer_trend,
    volunteer_service_types,
)
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

    tabs = st.tabs(["概览", "颗粒度同工", "同工明细"])

    with tabs[0]:
        agg = load_aggregations(granularity=granularity)
        if agg is None or agg.empty:
            st.info("暂无数据，请先点击左侧手动刷新。")
        else:
            st.subheader("总体趋势")
            st.line_chart(agg.set_index("period")["service_count"])
            st.dataframe(agg)

    with tabs[1]:
        part = load_participants_table(granularity=granularity)
        if part is None or part.empty:
            st.info("暂无数据")
        else:
            # 汇总每个 period 下的参与同工列表与人数
            grouped = part.groupby("period").agg(
                volunteers=("volunteer", lambda x: sorted(set(x))),
                volunteers_count=("volunteer", lambda x: len(set(x))),
            )
            grouped["volunteers"] = grouped["volunteers"].apply(lambda lst: ", ".join(lst))
            st.dataframe(grouped.reset_index())

    with tabs[2]:
        volunteers = list_volunteers()
        if not volunteers:
            st.info("暂无同工数据")
        else:
            selected = st.multiselect("选择同工", volunteers)
            for v in selected:
                st.markdown(f"**{v}** 的服事频率趋势")
                trend_df = volunteer_trend(v, granularity=granularity)
                if trend_df is None or trend_df.empty:
                    st.write("无数据")
                else:
                    st.line_chart(trend_df.set_index("period")["service_count"])
                st.markdown(f"**{v}** 的服事类型分布（按时间颗粒度）")
                dist_df = volunteer_service_types(v, granularity=granularity)
                if dist_df is None or dist_df.empty:
                    st.write("无数据")
                else:
                    pivot = dist_df.pivot(index="period", columns="service_type_id", values="service_count").fillna(0)
                    st.bar_chart(pivot)


if __name__ == "__main__":
    main()


