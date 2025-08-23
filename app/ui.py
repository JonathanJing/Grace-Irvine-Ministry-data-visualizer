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

    load_service_type_distribution_recent,
    load_volunteer_count_trend,
    load_cumulative_participation,
    load_individual_volunteer_trends,
    load_volunteer_join_leave_analysis,
    load_participation_distribution,
    load_service_stats_for_boxplot,
    load_volunteer_service_network,
    load_period_comparison_stats,
    # 桑基图数据加载函数
    load_service_transitions_for_sankey,
    load_volunteer_journey_sankey,
    load_seasonal_service_flow,
    load_experience_progression_sankey,
)
from jobs.ingest_job import run_ingest
from app.visualizations import (
    create_volunteer_ranking_chart,
    create_service_type_pie_chart,

    create_comparison_chart,
    display_volunteer_insights,
    display_top_performers_table,
    # 新增可视化功能
    create_volunteer_count_trend_chart,
    create_cumulative_participation_chart,
    create_individual_volunteer_trends_chart,
    create_volunteer_join_leave_chart,
    create_participation_distribution_chart,
    create_service_boxplot,
    create_period_comparison_chart,
    create_volunteer_service_network,
    display_advanced_insights,
    # 桑基图可视化功能
    create_service_transition_sankey,
    create_volunteer_journey_sankey,
    create_seasonal_flow_sankey,
    create_experience_progression_sankey,
    display_sankey_insights,
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

    tabs = st.tabs(["概览", "同工排行榜", "互动分析", "📊 总体概况", "🔍 深度分析", "📈 增减分析", "🌐 关系网络", "🌊 桑基流动图", "颗粒度同工", "同工明细", "原始数据"])

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
            ["服务类型分布"],
            key="analysis_type"
        )
        
        # 时间范围选择
        weeks_range = st.slider("选择分析周数", min_value=4, max_value=24, value=12, step=2)
        
        if analysis_option == "服务类型分布":
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
        


    with tabs[3]:  # 📊 总体概况
        st.header("📊 总体概况分析")
        st.markdown("### 查看同工总人数趋势和累计参与情况")
        
        # 时间粒度选择
        trend_granularity = st.selectbox(
            "选择时间粒度", 
            ["month", "quarter", "week"], 
            index=0,
            key="trend_granularity"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 同工总人数趋势
            volunteer_count_df = load_volunteer_count_trend(trend_granularity)
            if volunteer_count_df is not None and not volunteer_count_df.empty:
                fig_count = create_volunteer_count_trend_chart(
                    volunteer_count_df, 
                    f"🧑‍🤝‍🧑 同工总人数趋势 ({trend_granularity})"
                )
                st.plotly_chart(fig_count, use_container_width=True)
            else:
                st.info("暂无同工人数趋势数据")
        
        with col2:
            # 累计参与次数
            cumulative_df = load_cumulative_participation(trend_granularity)
            if cumulative_df is not None and not cumulative_df.empty:
                fig_cumulative = create_cumulative_participation_chart(
                    cumulative_df, 
                    f"📈 累计参与次数分析 ({trend_granularity})"
                )
                st.plotly_chart(fig_cumulative, use_container_width=True)
            else:
                st.info("暂无累计参与数据")

    with tabs[4]:  # 🔍 深度分析
        st.header("🔍 深度数据分析")
        st.markdown("### 个人参与情况和综合对比分析")
        
        # 分析参数设置
        col1, col2 = st.columns(2)
        with col1:
            analysis_weeks = st.slider("分析周数", min_value=4, max_value=24, value=12, key="analysis_weeks")
        with col2:
            top_volunteers_count = st.slider("显示前N名同工", min_value=5, max_value=20, value=10, key="top_volunteers")
        
        # 个人事工趋势分析
        st.subheader("📈 个人事工次数趋势")
        individual_trends_df = load_individual_volunteer_trends(top_volunteers_count, analysis_weeks)
        if individual_trends_df is not None and not individual_trends_df.empty:
            fig_individual = create_individual_volunteer_trends_chart(
                individual_trends_df, 
                f"🏃‍♂️ 前{top_volunteers_count}名同工个人事工趋势 (最近{analysis_weeks}周)"
            )
            st.plotly_chart(fig_individual, use_container_width=True)
        else:
            st.info("暂无个人趋势数据")
        
        # 参与次数分布和箱型图
        st.subheader("📊 参与次数分布分析")
        col1, col2 = st.columns(2)
        
        with col1:
            # 参与次数分布直方图
            distribution_df = load_participation_distribution(analysis_weeks)
            if distribution_df is not None and not distribution_df.empty:
                fig_dist = create_participation_distribution_chart(
                    distribution_df, 
                    f"📊 参与次数分布 (最近{analysis_weeks}周)"
                )
                st.plotly_chart(fig_dist, use_container_width=True)
            else:
                st.info("暂无分布数据")
        
        with col2:
            # 箱型图
            boxplot_df = load_service_stats_for_boxplot(analysis_weeks)
            if boxplot_df is not None and not boxplot_df.empty:
                fig_box = create_service_boxplot(
                    boxplot_df, 
                    f"📦 事工次数统计箱型图 (最近{analysis_weeks}周)"
                )
                st.plotly_chart(fig_box, use_container_width=True)
            else:
                st.info("暂无箱型图数据")
        
        # 高级数据洞察
        if distribution_df is not None and boxplot_df is not None:
            display_advanced_insights(boxplot_df, distribution_df)

    with tabs[5]:  # 📈 增减分析
        st.header("📈 增减分析")
        st.markdown("### 同工新增/离开情况和环比变化分析")
        
        # 分析参数
        comparison_weeks = st.slider("环比分析周数", min_value=2, max_value=12, value=4, key="comparison_weeks")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 同工新增/离开分析
            st.subheader("👥 同工新增/离开分析")
            join_leave_df = load_volunteer_join_leave_analysis("month")
            if join_leave_df is not None and not join_leave_df.empty:
                fig_join_leave = create_volunteer_join_leave_chart(
                    join_leave_df, 
                    "🔄 同工新增/减少分析 (按月)"
                )
                st.plotly_chart(fig_join_leave, use_container_width=True)
                
                # 显示详细数据表格
                with st.expander("查看详细数据"):
                    display_df = join_leave_df.copy()
                    display_df.columns = ['时期', '活跃同工', '新增同工', '上期活跃同工', '净变化']
                    st.dataframe(display_df, use_container_width=True)
            else:
                st.info("暂无新增/离开数据")
        
        with col2:
            # 环比变化分析
            st.subheader("📊 环比变化分析")
            comparison_df = load_period_comparison_stats(comparison_weeks)
            if comparison_df is not None and not comparison_df.empty:
                fig_comparison = create_period_comparison_chart(
                    comparison_df, 
                    f"📈 同工事工环比变化 ({comparison_weeks}周对比)", 
                    comparison_weeks
                )
                st.plotly_chart(fig_comparison, use_container_width=True)
                
                # 显示环比变化统计
                st.subheader("🔢 环比变化统计")
                increases = (comparison_df['change_amount'] > 0).sum()
                decreases = (comparison_df['change_amount'] < 0).sum()
                unchanged = (comparison_df['change_amount'] == 0).sum()
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("增长", f"{increases} 人", f"+{increases}")
                with col_b:
                    st.metric("下降", f"{decreases} 人", f"-{decreases}")
                with col_c:
                    st.metric("不变", f"{unchanged} 人", "")
            else:
                st.info("暂无环比数据")

    with tabs[6]:  # 🌐 关系网络
        st.header("🌐 关系网络分析")
        st.markdown("### 同工与事工类型的关系网络图")
        
        # 网络分析参数
        min_collaboration = st.slider(
            "最小合作次数 (过滤显示)", 
            min_value=1, max_value=10, value=3, 
            key="min_collaboration",
            help="只显示合作次数大于等于此值的关系"
        )
        
        # 加载网络数据
        network_df = load_volunteer_service_network(min_collaboration)
        if network_df is not None and not network_df.empty:
            fig_network = create_volunteer_service_network(
                network_df, 
                f"🕸️ 同工-事工关系网络 (最少{min_collaboration}次合作)"
            )
            st.plotly_chart(fig_network, use_container_width=True)
            
            # 网络统计信息
            st.subheader("📊 网络统计")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                unique_volunteers = network_df['volunteer_id'].nunique()
                st.metric("参与同工数", f"{unique_volunteers} 人")
            
            with col2:
                unique_services = network_df['service_type_id'].nunique()
                st.metric("事工类型数", f"{unique_services} 种")
            
            with col3:
                total_collaborations = len(network_df)
                st.metric("合作关系数", f"{total_collaborations} 个")
            
            with col4:
                avg_collaboration = network_df['collaboration_count'].mean()
                st.metric("平均合作次数", f"{avg_collaboration:.1f} 次")
            
            # 显示详细网络数据
            with st.expander("查看网络详细数据"):
                display_network_df = network_df.copy()
                display_network_df.columns = ['同工', '事工类型', '合作次数']
                display_network_df = display_network_df.sort_values('合作次数', ascending=False)
                st.dataframe(display_network_df, use_container_width=True)
        else:
            st.info(f"暂无网络数据 (最小合作次数: {min_collaboration})")
            st.caption("💡 提示：尝试降低最小合作次数以显示更多关系")

    with tabs[7]:  # 🌊 桑基流动图
        st.header("🌊 桑基流动图分析")
        st.markdown("### 同工随时间的流动和转换可视化")
        
        # 桑基图类型选择
        sankey_type = st.selectbox(
            "选择桑基图类型",
            [
                "事工类型转换", 
                "参与度演变", 
                "季节性流动", 
                "经验进阶路径"
            ],
            key="sankey_type"
        )
        
        # 根据选择的类型显示不同的桑基图
        if sankey_type == "事工类型转换":
            st.subheader("🔄 事工类型转换桑基图")
            st.markdown("显示同工在不同事工类型之间的月度转换流动")
            
            # 参数控制
            transition_months = st.slider(
                "分析月数", 
                min_value=3, max_value=12, value=6, 
                key="transition_months"
            )
            
            # 加载数据并显示图表
            transitions_df = load_service_transitions_for_sankey(transition_months)
            if transitions_df is not None and not transitions_df.empty:
                fig_transitions = create_service_transition_sankey(
                    transitions_df, 
                    f"🔄 事工类型转换流动图 (最近{transition_months}个月)"
                )
                st.plotly_chart(fig_transitions, use_container_width=True)
                
                # 显示详细数据
                with st.expander("查看转换详细数据"):
                    display_df = transitions_df.copy()
                    display_df.columns = ['源事工', '目标事工', '转换次数', '涉及同工数', '同工列表']
                    st.dataframe(display_df, use_container_width=True)
            else:
                st.info(f"暂无事工转换数据 (最近{transition_months}个月)")
        
        elif sankey_type == "参与度演变":
            st.subheader("📈 参与度演变桑基图")
            st.markdown("显示同工参与度水平的月度变化流动")
            
            # 参数控制
            journey_periods = st.slider(
                "分析时间段数", 
                min_value=3, max_value=12, value=6, 
                key="journey_periods"
            )
            
            # 加载数据并显示图表
            journey_df = load_volunteer_journey_sankey(journey_periods)
            if journey_df is not None and not journey_df.empty:
                fig_journey = create_volunteer_journey_sankey(
                    journey_df, 
                    f"📈 同工参与度演变流动图 (最近{journey_periods}个月)"
                )
                st.plotly_chart(fig_journey, use_container_width=True)
                
                # 显示详细数据
                with st.expander("查看参与度变化详细数据"):
                    display_df = journey_df.copy()
                    display_df.columns = ['源参与度', '目标参与度', '转换次数', '涉及同工数']
                    st.dataframe(display_df, use_container_width=True)
            else:
                st.info(f"暂无参与度演变数据 (最近{journey_periods}个月)")
        
        elif sankey_type == "季节性流动":
            st.subheader("🌍 季节性流动桑基图")
            st.markdown("显示同工在不同季节的事工分配模式")
            
            # 加载数据并显示图表
            seasonal_df = load_seasonal_service_flow()
            if seasonal_df is not None and not seasonal_df.empty:
                fig_seasonal = create_seasonal_flow_sankey(
                    seasonal_df, 
                    "🌍 季节性事工流动模式 (最近2年)"
                )
                st.plotly_chart(fig_seasonal, use_container_width=True)
                
                # 显示详细数据
                with st.expander("查看季节性流动详细数据"):
                    display_df = seasonal_df.copy()
                    display_df.columns = ['源季节-事工', '目标季节-事工', '流动次数', '涉及同工数']
                    st.dataframe(display_df, use_container_width=True)
            else:
                st.info("暂无季节性流动数据")
        
        elif sankey_type == "经验进阶路径":
            st.subheader("🎯 经验进阶路径桑基图")
            st.markdown("显示同工从技能类型到贡献级别的进阶路径")
            
            # 加载数据并显示图表
            experience_df = load_experience_progression_sankey()
            if experience_df is not None and not experience_df.empty:
                fig_experience = create_experience_progression_sankey(
                    experience_df, 
                    "🎯 同工经验进阶路径分析 (最近18个月)"
                )
                st.plotly_chart(fig_experience, use_container_width=True)
                
                # 显示详细数据
                with st.expander("查看进阶路径详细数据"):
                    display_df = experience_df.copy()
                    display_df.columns = ['同工类型', '贡献级别', '同工人数', '平均技能数']
                    st.dataframe(display_df, use_container_width=True)
            else:
                st.info("暂无经验进阶数据")
        
        # 综合洞察分析
        st.markdown("---")
        
        # 加载所有桑基图数据用于综合分析
        transitions_df = load_service_transitions_for_sankey(6)
        journey_df = load_volunteer_journey_sankey(6)
        seasonal_df = load_seasonal_service_flow()
        experience_df = load_experience_progression_sankey()
        
        display_sankey_insights(transitions_df, journey_df, seasonal_df, experience_df)
        
        # 桑基图使用说明
        with st.expander("📖 桑基图使用说明"):
            st.markdown("""
            ### 桑基图解读指南
            
            **🔄 事工类型转换桑基图**
            - 显示同工在不同月份主要参与的事工类型变化
            - 流量粗细表示转换的频率
            - 可以识别哪些事工容易相互转换
            
            **📈 参与度演变桑基图**
            - 根据每月参与次数将同工分为不同参与度级别
            - 显示同工参与度的提升或下降趋势
            - 帮助识别积极性变化模式
            
            **🌍 季节性流动桑基图**
            - 分析同工在不同季度的事工偏好
            - 可以发现季节性的事工需求变化
            - 有助于事工安排的季节性规划
            
            **🎯 经验进阶路径桑基图**
            - 展示同工技能类型与贡献级别的关系
            - 专精型：专注单一事工类型
            - 双技能型：精通两种事工类型
            - 多才型：参与三种或以上事工类型
            """)

    with tabs[8]:  # 颗粒度同工 (原来的 tabs[7])
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

    with tabs[9]:  # 同工明细 (原来的 tabs[8])
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

    with tabs[10]:  # 原始数据 (原来的 tabs[9])
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


