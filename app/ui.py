import streamlit as st
import pandas as pd
from metrics.aggregations import (
    load_aggregations,
    load_participants_table,
    list_volunteers,
    volunteer_trend,
    volunteer_service_types,
    load_raw_data,
)
from jobs.ingest_job import run_ingest


st.set_page_config(page_title="Ministry Data Visualizer", layout="wide")


def main() -> None:
    st.title("同工分析 App")
    st.caption("数据源：Google Sheet 事工总表 | 后端：DuckDB")
    
    # 显示数据截止日期
    from datetime import date
    current_date = date.today()
    st.info(f"📅 数据显示截止日期：{current_date.strftime('%Y年%m月%d日')}")

    with st.sidebar:
        st.header("控制台")
        if st.button("手动刷新（读取 Google Sheet）"):
            with st.spinner("正在刷新数据..."):
                run_ingest()
            st.success("刷新完成")

        granularity = st.selectbox("时间颗粒度", ["year", "quarter", "month"], index=2)

    tabs = st.tabs(["概览", "颗粒度同工", "同工明细", "原始数据"])

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

    with tabs[3]:
        st.subheader("原始数据")
        st.caption("从Google Sheet提取并清洗后的所有服事记录")
        
        raw_data = load_raw_data()
        if raw_data is None or raw_data.empty:
            st.info("暂无数据，请先点击左侧手动刷新。")
        else:
            # 显示数据统计信息
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总记录数", len(raw_data))
            with col2:
                st.metric("同工数量", raw_data["volunteer_id"].nunique())
            with col3:
                st.metric("服务类型数", raw_data["service_type_id"].nunique())
            with col4:
                st.metric("日期范围", f"{raw_data['service_date'].min().strftime('%Y-%m-%d')} 至 {raw_data['service_date'].max().strftime('%Y-%m-%d')}")
            
            # 添加筛选功能
            st.subheader("数据筛选")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                volunteers = sorted(raw_data["volunteer_id"].unique())
                selected_volunteers = st.multiselect("选择同工", volunteers, default=volunteers[:5] if len(volunteers) > 5 else volunteers)
            
            with col2:
                service_types = sorted(raw_data["service_type_id"].unique())
                selected_service_types = st.multiselect("选择服务类型", service_types, default=service_types)
            
            with col3:
                date_range = st.date_input(
                    "选择日期范围",
                    value=(raw_data["service_date"].min(), raw_data["service_date"].max()),
                    min_value=raw_data["service_date"].min(),
                    max_value=raw_data["service_date"].max()
                )
            
            # 应用筛选
            filtered_data = raw_data.copy()
            if selected_volunteers:
                filtered_data = filtered_data[filtered_data["volunteer_id"].isin(selected_volunteers)]
            if selected_service_types:
                filtered_data = filtered_data[filtered_data["service_type_id"].isin(selected_service_types)]
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_data = filtered_data[
                    (filtered_data["service_date"] >= pd.Timestamp(start_date)) &
                    (filtered_data["service_date"] <= pd.Timestamp(end_date))
                ]
            
            st.subheader(f"筛选结果 ({len(filtered_data)} 条记录)")
            
            # 显示数据表格
            if not filtered_data.empty:
                # 格式化日期列
                display_data = filtered_data.copy()
                display_data["service_date"] = display_data["service_date"].dt.strftime("%Y-%m-%d")
                display_data["ingested_at"] = display_data["ingested_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
                
                # 重新排列列顺序
                display_data = display_data[[
                    "service_date", "volunteer_id", "service_type_id", 
                    "fact_id", "source_row_id", "ingested_at",
                    "year", "quarter", "month"
                ]]
                
                st.dataframe(
                    display_data,
                    use_container_width=True,
                    hide_index=True
                )
                
                # 添加下载按钮
                csv = display_data.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 下载CSV文件",
                    data=csv,
                    file_name=f"ministry_raw_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("没有符合筛选条件的数据")


if __name__ == "__main__":
    main()


