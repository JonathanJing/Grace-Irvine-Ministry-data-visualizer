import streamlit as st
import pandas as pd
from metrics.aggregations import (
    load_aggregations,
    load_participants_table,
    list_volunteers,
    volunteer_trend,
    volunteer_service_types,
    load_raw_data,
    load_volunteer_stats_recent_weeks,
    load_volunteer_stats_recent_quarter,
    load_volunteer_weekly_trend,
    load_service_type_distribution_recent,
)
from jobs.ingest_job import run_ingest
from app.visualizations import (
    create_volunteer_ranking_chart,
    create_service_type_pie_chart,
    create_weekly_trend_chart,
    create_volunteer_heatmap,
    create_comparison_chart,
    display_volunteer_insights,
    display_top_performers_table,
)


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

    tabs = st.tabs(["概览", "同工排行榜", "互动分析", "颗粒度同工", "同工明细", "原始数据"])

    with tabs[0]:
        agg = load_aggregations(granularity=granularity)
        if agg is None or agg.empty:
            st.info("暂无数据，请先点击左侧手动刷新。")
        else:
            st.subheader("总体趋势")
            st.line_chart(agg.set_index("period")["service_count"])
            st.dataframe(agg)

    with tabs[1]:
        st.header("🏆 同工排行榜")
        st.markdown("### 查看最近4周和最近一季度哪个同工事工最多")
        
        # 加载数据
        recent_4w_df = load_volunteer_stats_recent_weeks(4)
        recent_quarter_df = load_volunteer_stats_recent_quarter()
        
        # 显示数据时间范围信息
        from datetime import date, timedelta
        current_date = date.today()
        four_weeks_ago = current_date - timedelta(weeks=4)
        three_months_ago = current_date - timedelta(days=90)  # 约3个月
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📅 最近4周范围：{four_weeks_ago.strftime('%Y-%m-%d')} 至 {current_date.strftime('%Y-%m-%d')}")
        with col2:
            st.info(f"📅 最近一季度范围：{three_months_ago.strftime('%Y-%m-%d')} 至 {current_date.strftime('%Y-%m-%d')}")
        
        # 显示实际数据范围
        if recent_4w_df is not None and not recent_4w_df.empty:
            actual_range_4w = f"{recent_4w_df['first_service_date'].min().strftime('%Y-%m-%d')} 至 {recent_4w_df['last_service_date'].max().strftime('%Y-%m-%d')}"
            st.caption(f"💡 最近4周实际数据范围：{actual_range_4w}")
        
        if recent_quarter_df is not None and not recent_quarter_df.empty:
            actual_range_quarter = f"{recent_quarter_df['first_service_date'].min().strftime('%Y-%m-%d')} 至 {recent_quarter_df['last_service_date'].max().strftime('%Y-%m-%d')}"
            st.caption(f"💡 最近一季度实际数据范围：{actual_range_quarter}")
        
        if (recent_4w_df is None or recent_4w_df.empty) and (recent_quarter_df is None or recent_quarter_df.empty):
            st.info("暂无数据，请先点击左侧手动刷新。")
        else:
            # 显示洞察信息
            display_volunteer_insights(recent_4w_df, recent_quarter_df)
            
            st.markdown("---")
            
            # 创建两列布局
            col1, col2 = st.columns(2)
            
            with col1:
                if recent_4w_df is not None and not recent_4w_df.empty:
                    # 4周排行榜图表
                    fig_4w = create_volunteer_ranking_chart(
                        recent_4w_df, 
                        "🔥 最近4周", 
                        "最近4周"
                    )
                    st.plotly_chart(fig_4w, use_container_width=True)
                    
                    # 4周排行榜表格
                    display_top_performers_table(
                        recent_4w_df, 
                        "🏅 最近4周排行榜", 
                        "最近4周"
                    )
                else:
                    st.warning("暂无最近4周数据")
            
            with col2:
                if recent_quarter_df is not None and not recent_quarter_df.empty:
                    # 季度排行榜图表
                    fig_quarter = create_volunteer_ranking_chart(
                        recent_quarter_df, 
                        "📈 最近一季度", 
                        "最近一季度"
                    )
                    st.plotly_chart(fig_quarter, use_container_width=True)
                    
                    # 季度排行榜表格
                    display_top_performers_table(
                        recent_quarter_df, 
                        "🏅 最近一季度排行榜", 
                        "最近一季度"
                    )
                else:
                    st.warning("暂无最近一季度数据")
            
            # 对比图表
            st.markdown("---")
            st.subheader("📊 4周 vs 季度对比")
            if (recent_4w_df is not None and not recent_4w_df.empty) or (recent_quarter_df is not None and not recent_quarter_df.empty):
                fig_comparison = create_comparison_chart(recent_4w_df, recent_quarter_df)
                st.plotly_chart(fig_comparison, use_container_width=True)
            else:
                st.info("暂无对比数据")

    with tabs[2]:
        st.header("📊 互动分析")
        st.markdown("### 深度分析同工参与趋势和服务类型分布")
        
        # 分析选项
        analysis_option = st.selectbox(
            "选择分析类型",
            ["每周趋势分析", "服务类型分布", "同工活跃度热力图"],
            key="analysis_type"
        )
        
        # 时间范围选择
        weeks_range = st.slider("选择分析周数", min_value=4, max_value=24, value=12, step=2)
        
        if analysis_option == "每周趋势分析":
            weekly_trend_df = load_volunteer_weekly_trend(weeks_range)
            if weekly_trend_df is not None and not weekly_trend_df.empty:
                fig_trend = create_weekly_trend_chart(
                    weekly_trend_df, 
                    f"📈 最近{weeks_range}周事工趋势分析"
                )
                st.plotly_chart(fig_trend, use_container_width=True)
                
                # 显示详细数据
                with st.expander("查看详细数据"):
                    st.dataframe(weekly_trend_df, use_container_width=True)
            else:
                st.info("暂无趋势数据")
        
        elif analysis_option == "服务类型分布":
            service_dist_df = load_service_type_distribution_recent(weeks_range)
            if service_dist_df is not None and not service_dist_df.empty:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    fig_pie = create_service_type_pie_chart(
                        service_dist_df, 
                        f"🎯 最近{weeks_range}周服务类型分布"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    st.subheader("📋 分布详情")
                    for _, row in service_dist_df.iterrows():
                        st.metric(
                            row['service_type_id'],
                            f"{row['total_services']} 次",
                            f"{row['unique_volunteers']} 人参与"
                        )
            else:
                st.info("暂无分布数据")
        
        elif analysis_option == "同工活跃度热力图":
            weekly_trend_df = load_volunteer_weekly_trend(weeks_range)
            if weekly_trend_df is not None and not weekly_trend_df.empty:
                fig_heatmap = create_volunteer_heatmap(
                    weekly_trend_df, 
                    f"🔥 最近{weeks_range}周同工活跃度热力图"
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                st.info("💡 提示：颜色越深表示该同工在该周的事工次数越多")
            else:
                st.info("暂无活跃度数据")

    with tabs[3]:
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

    with tabs[4]:
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

    with tabs[5]:
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


