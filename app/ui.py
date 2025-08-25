import streamlit as st
import pandas as pd
from metrics.aggregations import (
    load_participants_table,
    list_volunteers,
    volunteer_trend,
    volunteer_service_types,
    load_raw_data,
    load_volunteer_stats_recent_weeks,
    load_volunteer_stats_recent_quarter,
    load_volunteer_count_trend,
    load_volunteer_join_leave_analysis,
    load_period_comparison_stats,
    # 新桑基图数据加载函数
    load_volunteer_ministry_flow_data,
    get_available_ministries,
    # 新增：总体概况数据加载函数
    load_data_time_range,
    load_worker_participation_overview,
    load_worker_burden_distribution,
    load_service_category_distribution,
    load_monthly_activity_heatmap,
)
from jobs.ingest_job import run_ingest
from app.visualizations import (
    create_volunteer_ranking_chart,


    create_comparison_chart,
    display_volunteer_insights,
    display_top_performers_table,
    # 新增可视化功能
    create_volunteer_count_trend_chart,


    create_volunteer_join_leave_chart,


    create_period_comparison_chart,


    # 新桑基图可视化功能
    create_volunteer_ministry_flow_sankey,
    create_simplified_ministry_flow,
    display_ministry_flow_insights,
    # 新增：总体概况可视化功能
    display_data_time_range,
    display_worker_participation_overview,
    create_worker_burden_distribution_chart,
    create_service_category_pie_chart,
    create_monthly_activity_heatmap,
)


st.set_page_config(page_title="Ministry Data Visualizer", layout="wide")


def main() -> None:
    # 头部信息和控制按钮
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("同工分析 App")
        st.caption("数据源：Google Sheet 事工总表 | 后端：DuckDB")
    
    with col2:
        st.write("")  # 添加一些垂直空间对齐
        if st.button("🔄 手动刷新数据", 
                    help="点击从 Google Sheet 读取最新数据",
                    type="primary",
                    use_container_width=True):
            with st.spinner("正在刷新数据..."):
                run_ingest()
            st.success("✅ 刷新完成")
    
    # 显示数据截止日期
    from datetime import date
    current_date = date.today()
    st.info(f"📅 数据显示截止日期：{current_date.strftime('%Y年%m月%d日')}")
    
    st.divider()  # 添加分隔线

    tabs = st.tabs(["同工排行榜", "📊 总体概况", "📈 增减分析", "🌊 事工流动", "参与统计", "同工明细", "原始数据"])

    with tabs[0]:
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

    with tabs[1]:  # 📊 总体概况
        st.header("📊 总体概况分析")
        st.markdown("### 全面了解事工数据概况和关键指标")
        
        # 1. 数据时间范围与周期
        time_range_info = load_data_time_range()
        if time_range_info:
            display_data_time_range(time_range_info)
        else:
            st.info("暂无时间范围数据")
        
        st.divider()
        
        # 2. 同工总体参与情况
        participation_info = load_worker_participation_overview()
        if participation_info:
            display_worker_participation_overview(participation_info)
        else:
            st.info("暂无参与情况数据")
        
        st.divider()
        
        # 3. 双列布局：同工负担分布 + 事工类别分布
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⚖️ 同工参与负担分析")
            burden_df = load_worker_burden_distribution()
            if burden_df is not None and not burden_df.empty:
                fig_burden = create_worker_burden_distribution_chart(burden_df)
                st.plotly_chart(fig_burden, use_container_width=True)
                
                # 显示负担分析洞察
                avg_services = burden_df['total_services'].mean()
                max_services = burden_df['total_services'].max()
                min_services = burden_df['total_services'].min()
                
                st.caption(f"💡 **负担分析：** 平均事工次数 {avg_services:.1f}，最高 {max_services}，最低 {min_services}")
                
                # 检查是否有高负担同工（超过平均值2倍）
                high_burden_threshold = avg_services * 2
                high_burden_workers = burden_df[burden_df['total_services'] > high_burden_threshold]
                if not high_burden_workers.empty:
                    st.warning(f"⚠️ 发现 {len(high_burden_workers)} 位高负担同工（事工次数超过平均值2倍）")
            else:
                st.info("暂无负担分布数据")
        
        with col2:
            st.subheader("📊 事工类别分布")
            category_df = load_service_category_distribution()
            if category_df is not None and not category_df.empty:
                fig_category = create_service_category_pie_chart(category_df)
                st.plotly_chart(fig_category, use_container_width=True)
                
                # 显示类别分析洞察
                total_categories = len(category_df)
                most_popular = category_df.iloc[0]['service_type']
                most_popular_count = category_df.iloc[0]['total_services']
                
                st.caption(f"💡 **类别分析：** 共 {total_categories} 种事工类型，最热门：{most_popular}（{most_popular_count}次）")
            else:
                st.info("暂无类别分布数据")
        
        st.divider()
        
        # 4. 时间趋势与季节性分析
        st.subheader("📈 时间趋势与季节性分析")
        monthly_df = load_monthly_activity_heatmap()
        if monthly_df is not None and not monthly_df.empty:
            fig_monthly = create_monthly_activity_heatmap(monthly_df)
            st.plotly_chart(fig_monthly, use_container_width=True)
            
            # 显示趋势洞察
            if len(monthly_df) >= 2:
                recent_services = monthly_df.iloc[-1]['total_services']
                previous_services = monthly_df.iloc[-2]['total_services']
                trend = "📈 上升" if recent_services > previous_services else "📉 下降" if recent_services < previous_services else "➡️ 持平"
                change_percent = ((recent_services - previous_services) / previous_services * 100) if previous_services > 0 else 0
                
                st.caption(f"💡 **趋势分析：** 最近月份事工活动呈{trend}趋势（变化{change_percent:+.1f}%）")
        else:
            st.info("暂无月度活动数据")
        
        st.divider()
        
        # 5. 保留原有的同工总人数趋势（作为补充）
        st.subheader("👥 同工总人数趋势 (按月)")
        volunteer_count_df = load_volunteer_count_trend()
        if volunteer_count_df is not None and not volunteer_count_df.empty:
            fig_count = create_volunteer_count_trend_chart(
                volunteer_count_df, 
                "🧑‍🤝‍🧑 同工总人数趋势 (按月)"
            )
            st.plotly_chart(fig_count, use_container_width=True)
        else:
            st.info("暂无同工人数趋势数据")

    with tabs[2]:  # 📈 增减分析
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

    with tabs[3]:  # 🌊 事工流动
        st.header("🌊 同工事工流动分析")
        st.markdown("### 专注展示每个同工每个月在各种事工中的流动情况")
        
        # 设置参数
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 日期范围选择
            from datetime import date, timedelta
            end_date = date.today()
            start_date = end_date - timedelta(days=180)  # 默认6个月
            
            date_range = st.date_input(
                "选择分析日期范围",
                value=(start_date, end_date),
                key="flow_date_range"
            )
            
            if len(date_range) == 2:
                start_str = date_range[0].strftime('%Y-%m-%d')
                end_str = date_range[1].strftime('%Y-%m-%d')
            else:
                start_str = start_date.strftime('%Y-%m-%d')
                end_str = end_date.strftime('%Y-%m-%d')
        
        with col2:
            # 同工选择
            volunteers = list_volunteers()
            if volunteers:
                selected_volunteers = st.multiselect(
                    "选择同工（留空显示所有）",
                    volunteers,
                    default=[],
                    key="flow_volunteers",
                    help="选择要分析的同工，留空则分析所有同工"
                )
            else:
                st.info("暂无同工数据")
                selected_volunteers = []
        
        with col3:
            # 分析选项
            analysis_mode = st.selectbox(
                "分析模式",
                ["流动桑基图", "简化流向"],
                key="analysis_mode",
                help="选择分析展示方式"
            )
        
        # 生成分析按钮
        if st.button("🔍 生成事工流动分析", key="generate_flow"):
            with st.spinner("正在分析同工事工流动..."):
                
                # 显示调试信息
                st.info(f"""
                🔍 **分析参数：**
                - 日期范围：{start_str} 至 {end_str}
                - 选中同工：{len(selected_volunteers) if selected_volunteers else 0} 人 
                  ({', '.join(selected_volunteers[:5]) + ('...' if len(selected_volunteers) > 5 else '') if selected_volunteers else '全部同工'})
                """)
                
                # 加载流动数据
                flow_data = load_volunteer_ministry_flow_data(
                    start_date=start_str,
                    end_date=end_str,
                    selected_volunteers=selected_volunteers if selected_volunteers else None
                )
                
                if flow_data is not None and not flow_data.empty:
                    st.success(f"📊 分析完成！共找到 {len(flow_data)} 条流动记录")
                    
                    if analysis_mode == "流动桑基图":
                        # 显示桑基图
                        fig = create_volunteer_ministry_flow_sankey(
                            flow_data, 
                            f"同工事工流动分析 ({start_str} 至 {end_str})"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    else:  # 简化流向
                        # 显示简化的流向分析
                        st.subheader("📈 简化流向分析")
                        
                        # 聚合流动数据
                        flow_summary = flow_data.groupby(['from_ministry', 'to_ministry']).agg({
                            'flow_intensity': 'sum',
                            'volunteer_name': lambda x: ', '.join(sorted(set(x)))
                        }).reset_index()
                        
                        flow_summary = flow_summary.sort_values('flow_intensity', ascending=False)
                        
                        # 重命名列
                        flow_summary.columns = ['来源事工', '目标事工', '流动人次', '涉及同工']
                        
                        # 添加流动类型标识
                        flow_summary['流动类型'] = flow_summary.apply(
                            lambda row: '稳定' if row['来源事工'] == row['目标事工'] else '转换', 
                            axis=1
                        )
                        
                        # 显示汇总表格
                        st.dataframe(
                            flow_summary[['流动类型', '来源事工', '目标事工', '流动人次', '涉及同工']],
                            use_container_width=True,
                            hide_index=True
                        )
                    
                    # 显示流动洞察
                    display_ministry_flow_insights(flow_data)
                    
                    # 详细数据查看
                    with st.expander("📋 查看详细流动数据"):
                        display_data = flow_data.copy()
                        display_data.columns = ['同工姓名', '来源月份', '目标月份', '来源事工', '目标事工', '流动强度']
                        st.dataframe(display_data, use_container_width=True, hide_index=True)
                        
                        # 下载数据
                        csv_data = display_data.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="📥 下载流动数据CSV",
                            data=csv_data,
                            file_name=f"ministry_flow_{start_str}_to_{end_str}.csv",
                            mime="text/csv"
                        )
                
                else:
                    # 提供更详细的调试信息
                    st.warning("⚠️ 在选定条件下暂无流动数据")
                    
                    # 显示调试信息
                    with st.expander("🔧 调试信息"):
                        # 检查基础数据
                        raw_data = load_raw_data()
                        all_volunteers = list_volunteers()
                        
                        if raw_data is None or raw_data.empty:
                            st.error("❌ 数据库中暂无任何服事记录，请先点击页面顶部的'🔄 手动刷新数据'按钮")
                        else:
                            st.info(f"✅ 数据库共有 {len(raw_data)} 条服事记录")
                            
                            # 检查日期范围内的数据
                            filtered_data = raw_data[
                                (raw_data['service_date'] >= pd.Timestamp(start_str)) &
                                (raw_data['service_date'] <= pd.Timestamp(end_str))
                            ]
                            
                            if filtered_data.empty:
                                st.warning(f"📅 在日期范围 {start_str} 至 {end_str} 内没有服事记录")
                                date_range = f"{raw_data['service_date'].min().strftime('%Y-%m-%d')} 至 {raw_data['service_date'].max().strftime('%Y-%m-%d')}"
                                st.info(f"💡 数据库中的日期范围：{date_range}")
                            else:
                                st.info(f"✅ 在指定日期范围内有 {len(filtered_data)} 条记录")
                                
                                # 检查选中的同工
                                if selected_volunteers:
                                    matching_volunteers = [v for v in selected_volunteers if v in filtered_data['volunteer_id'].values]
                                    if not matching_volunteers:
                                        st.warning(f"👥 选中的同工在指定日期范围内没有服事记录")
                                        available_volunteers = sorted(filtered_data['volunteer_id'].unique())
                                        st.info(f"💡 在此日期范围内有服事的同工：{', '.join(available_volunteers[:10])}{'...' if len(available_volunteers) > 10 else ''}")
                                    else:
                                        st.info(f"✅ 匹配的同工：{', '.join(matching_volunteers)}")
                                
                                # 显示月份分布
                                monthly_dist = filtered_data.groupby(filtered_data['service_date'].dt.to_period('M')).size()
                                st.info(f"📊 月份分布：{dict(monthly_dist)}")
                    
                    st.markdown("""
                    **💡 解决建议：**
                    1. 🔄 如果是首次使用，请点击页面顶部的"手动刷新数据"按钮
                    2. 📅 尝试扩大日期范围（建议至少3个月）
                    3. 👥 不选择特定同工，分析所有同工的流动
                    4. 📊 确保所选日期范围内有足够的服事记录
                    """)
        
        # 使用说明
        with st.expander("📖 使用说明"):
            st.markdown("""
            ### 同工事工流动分析说明
            
            **🎯 功能特点**
            - 专注分析每个同工每个月的主要事工变化
            - 通过桑基图直观展示流动模式
            - 支持选择特定同工或时间范围
            
            **📊 数据解释**
            - **节点**: 月份-事工组合（如 2024-12 招待）
            - **连线**: 同工从一个月的事工流向下个月的事工
            - **流动强度**: 每个同工的流动记录为1，多个同工则累加
            
            **⚙️ 分析选项**
            - **流动桑基图**: 完整的桑基流动图，适合全局分析
            - **简化流向**: 汇总表格形式，适合数据查看
            
            **💡 使用建议**
            1. 先选择合适的日期范围（建议3-6个月）
            2. 可选择特定同工进行focused分析
            3. 查看洞察指标了解整体流动情况
            4. 通过详细数据进行深度分析
            """)
        
        # 快速示例
        st.markdown("---")
        st.subheader("🚀 快速开始")
        st.markdown("""
        **推荐分析步骤：**
        1. 保持默认日期范围（最近6个月）
        2. 不选择特定同工（分析所有同工）
        3. 选择「流动桑基图」模式
        4. 点击「生成事工流动分析」按钮
        5. 查看流动洞察指标和详细数据
        """)

    with tabs[4]:  # 参与统计
        part = load_participants_table()
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

    with tabs[5]:  # 同工明细
        volunteers = list_volunteers()
        if not volunteers:
            st.info("暂无同工数据")
        else:
            selected = st.multiselect("选择同工", volunteers)
            for v in selected:
                st.markdown(f"**{v}** 的服事频率趋势")
                trend_df = volunteer_trend(v)
                if trend_df is None or trend_df.empty:
                    st.write("无数据")
                else:
                    st.line_chart(trend_df.set_index("period")["service_count"])
                st.markdown(f"**{v}** 的服事类型分布（按月统计）")
                dist_df = volunteer_service_types(v)
                if dist_df is None or dist_df.empty:
                    st.write("无数据")
                else:
                    pivot = dist_df.pivot(index="period", columns="service_type_id", values="service_count").fillna(0)
                    st.bar_chart(pivot)

    with tabs[6]:  # 原始数据
        st.subheader("原始数据")
        st.caption("从Google Sheet提取并清洗后的所有服事记录")
        
        raw_data = load_raw_data()
        if raw_data is None or raw_data.empty:
            st.info("暂无数据，请先点击上方手动刷新数据。")
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


