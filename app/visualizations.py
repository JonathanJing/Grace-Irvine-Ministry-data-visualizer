"""
高级数据可视化组件
提供互动图表显示同工事工统计
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
import networkx as nx
from typing import Optional


def create_volunteer_ranking_chart(df: pd.DataFrame, title: str, time_period: str) -> go.Figure:
    """创建同工事工排名条形图"""
    if df is None or df.empty:
        return go.Figure()
    
    # 取前15名同工
    top_volunteers = df.head(15).copy()
    
    # 创建颜色映射 - 前3名使用特殊颜色
    colors = ['#FFD700', '#C0C0C0', '#CD7F32'] + ['#4CAF50'] * 12  # 金银铜 + 绿色
    colors = colors[:len(top_volunteers)]
    
    fig = go.Figure()
    
    # 添加条形图
    fig.add_trace(go.Bar(
        y=top_volunteers['volunteer_id'],
        x=top_volunteers['total_services'],
        orientation='h',
        marker=dict(color=colors),
        text=top_volunteers['total_services'],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>' +
                      '事工次数: %{x}<br>' +
                      '服务类型: %{customdata}<br>' +
                      '<extra></extra>',
        customdata=top_volunteers['service_types']
    ))
    
    fig.update_layout(
        title=dict(
            text=f'{title}<br><sub>{time_period}同工事工排行榜 (Top 15)</sub>',
            x=0.5,
            font=dict(size=20)
        ),
        xaxis_title='事工次数',
        yaxis_title='同工姓名',
        height=600,
        yaxis=dict(categoryorder='total ascending'),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=120, r=50, t=100, b=50)
    )
    
    return fig








def create_comparison_chart(recent_4w_df: pd.DataFrame, recent_quarter_df: pd.DataFrame) -> go.Figure:
    """创建4周vs季度对比图"""
    if (recent_4w_df is None or recent_4w_df.empty) and (recent_quarter_df is None or recent_quarter_df.empty):
        return go.Figure()
    
    # 准备数据
    data_4w = recent_4w_df.head(10) if recent_4w_df is not None and not recent_4w_df.empty else pd.DataFrame()
    data_quarter = recent_quarter_df.head(10) if recent_quarter_df is not None and not recent_quarter_df.empty else pd.DataFrame()
    
    # 获取所有同工的并集
    all_volunteers = set()
    if not data_4w.empty:
        all_volunteers.update(data_4w['volunteer_id'].tolist())
    if not data_quarter.empty:
        all_volunteers.update(data_quarter['volunteer_id'].tolist())
    
    volunteers = sorted(list(all_volunteers))[:15]  # 限制显示数量
    
    # 创建对比数据
    services_4w = []
    services_quarter = []
    
    for volunteer in volunteers:
        # 4周数据
        if not data_4w.empty and volunteer in data_4w['volunteer_id'].values:
            services_4w.append(data_4w[data_4w['volunteer_id'] == volunteer]['total_services'].iloc[0])
        else:
            services_4w.append(0)
        
        # 季度数据
        if not data_quarter.empty and volunteer in data_quarter['volunteer_id'].values:
            services_quarter.append(data_quarter[data_quarter['volunteer_id'] == volunteer]['total_services'].iloc[0])
        else:
            services_quarter.append(0)
    
    fig = go.Figure()
    
    # 添加4周数据
    fig.add_trace(go.Bar(
        name='最近4周',
        y=volunteers,
        x=services_4w,
        orientation='h',
        marker=dict(color='#FF6B6B'),
        opacity=0.8
    ))
    
    # 添加季度数据
    fig.add_trace(go.Bar(
        name='最近一季度',
        y=volunteers,
        x=services_quarter,
        orientation='h',
        marker=dict(color='#4ECDC4'),
        opacity=0.8
    ))
    
    fig.update_layout(
        title=dict(
            text='同工事工对比：最近4周 vs 最近一季度',
            x=0.5,
            font=dict(size=18)
        ),
        xaxis_title='事工次数',
        yaxis_title='同工姓名',
        height=600,
        barmode='group',
        yaxis=dict(categoryorder='total ascending'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=120, r=50, t=100, b=50)
    )
    
    return fig


def display_volunteer_insights(recent_4w_df: pd.DataFrame, recent_quarter_df: pd.DataFrame):
    """显示同工洞察信息"""
    st.subheader("📊 数据洞察")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if recent_4w_df is not None and not recent_4w_df.empty:
            top_volunteer_4w = recent_4w_df.iloc[0]['volunteer_id']
            top_services_4w = recent_4w_df.iloc[0]['total_services']
            st.metric(
                "4周冠军",
                top_volunteer_4w,
                f"{top_services_4w} 次事工"
            )
        else:
            st.metric("4周冠军", "暂无数据", "")
    
    with col2:
        if recent_quarter_df is not None and not recent_quarter_df.empty:
            top_volunteer_quarter = recent_quarter_df.iloc[0]['volunteer_id']
            top_services_quarter = recent_quarter_df.iloc[0]['total_services']
            st.metric(
                "季度冠军",
                top_volunteer_quarter,
                f"{top_services_quarter} 次事工"
            )
        else:
            st.metric("季度冠军", "暂无数据", "")
    
    with col3:
        if recent_4w_df is not None and not recent_4w_df.empty:
            active_volunteers_4w = len(recent_4w_df)
            avg_services_4w = recent_4w_df['total_services'].mean()
            st.metric(
                "4周活跃同工",
                f"{active_volunteers_4w} 人",
                f"平均 {avg_services_4w:.1f} 次"
            )
        else:
            st.metric("4周活跃同工", "0 人", "")
    
    with col4:
        if recent_quarter_df is not None and not recent_quarter_df.empty:
            active_volunteers_quarter = len(recent_quarter_df)
            avg_services_quarter = recent_quarter_df['total_services'].mean()
            st.metric(
                "季度活跃同工",
                f"{active_volunteers_quarter} 人",
                f"平均 {avg_services_quarter:.1f} 次"
            )
        else:
            st.metric("季度活跃同工", "0 人", "")


def display_top_performers_table(df: pd.DataFrame, title: str, period: str):
    """显示顶级表现者表格"""
    if df is None or df.empty:
        st.warning(f"暂无{period}数据")
        return
    
    st.subheader(title)
    
    # 格式化数据
    display_df = df.head(10).copy()
    display_df['排名'] = range(1, len(display_df) + 1)
    display_df['同工姓名'] = display_df['volunteer_id']
    display_df['事工次数'] = display_df['total_services']
    display_df['服务类型数'] = display_df['service_types_count']
    display_df['服务类型'] = display_df['service_types']
    
    # 重新排列列
    display_df = display_df[['排名', '同工姓名', '事工次数', '服务类型数', '服务类型']]
    
    # 添加排名徽章
    def add_rank_badge(row):
        rank = row['排名']
        if rank == 1:
            return "🥇 " + str(rank)
        elif rank == 2:
            return "🥈 " + str(rank)
        elif rank == 3:
            return "🥉 " + str(rank)
        else:
            return str(rank)
    
    display_df['排名'] = display_df.apply(add_rank_badge, axis=1)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "排名": st.column_config.TextColumn("排名", width="small"),
            "同工姓名": st.column_config.TextColumn("同工姓名", width="medium"),
            "事工次数": st.column_config.NumberColumn("事工次数", width="small"),
            "服务类型数": st.column_config.NumberColumn("服务类型数", width="small"),
            "服务类型": st.column_config.TextColumn("服务类型", width="large")
        }
    )


# =============================================================================
# 新增可视化功能
# =============================================================================

def create_volunteer_count_trend_chart(df: pd.DataFrame, title: str) -> go.Figure:
    """创建同工总人数趋势折线图"""
    if df is None or df.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    # 添加同工人数趋势线
    fig.add_trace(go.Scatter(
        x=df['period'],
        y=df['volunteer_count'],
        mode='lines+markers',
        name='活跃同工人数',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>' +
                      '活跃同工: %{y}人<br>' +
                      '总事工次数: %{customdata}<br>' +
                      '<extra></extra>',
        customdata=df['total_services']
    ))
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=18)
        ),
        xaxis_title='时间',
        yaxis_title='同工人数',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        showlegend=False
    )
    
    return fig


def create_cumulative_participation_chart(df: pd.DataFrame, title: str) -> go.Figure:
    """创建累计参与次数图表（柱状图+面积图）"""
    if df is None or df.empty:
        return go.Figure()
    
    # 创建子图
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('期间事工次数', '累计事工次数'),
        vertical_spacing=0.15
    )
    
    # 添加期间事工次数柱状图
    fig.add_trace(go.Bar(
        x=df['period'],
        y=df['period_services'],
        name='期间事工次数',
        marker=dict(color='#ff7f0e'),
        hovertemplate='<b>%{x}</b><br>期间事工: %{y}次<extra></extra>'
    ), row=1, col=1)
    
    # 添加累计事工次数面积图
    fig.add_trace(go.Scatter(
        x=df['period'],
        y=df['cumulative_services'],
        mode='lines',
        fill='tonexty',
        name='累计事工次数',
        line=dict(color='#2ca02c', width=2),
        fillcolor='rgba(44, 160, 44, 0.3)',
        hovertemplate='<b>%{x}</b><br>累计事工: %{y}次<extra></extra>'
    ), row=2, col=1)
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=18)
        ),
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        showlegend=False
    )
    
    # 更新x轴标签角度
    fig.update_xaxes(tickangle=45)
    
    return fig





def create_volunteer_join_leave_chart(df: pd.DataFrame, title: str) -> go.Figure:
    """创建同工新增/离开堆叠柱状图"""
    if df is None or df.empty:
        return go.Figure()
    
    # Create a copy to avoid modifying the original DataFrame
    df_copy = df.copy()
    
    fig = go.Figure()
    
    # 添加新增同工
    fig.add_trace(go.Bar(
        x=df_copy['period'],
        y=df_copy['new_volunteers'],
        name='新增同工',
        marker=dict(color='#2ca02c'),
        hovertemplate='<b>%{x}</b><br>新增同工: %{y}人<extra></extra>'
    ))
    
    # 计算离开同工（如果净变化为负数）
    df_copy['left_volunteers'] = df_copy['net_change'].apply(lambda x: abs(x) if x < 0 else 0)
    
    fig.add_trace(go.Bar(
        x=df_copy['period'],
        y=df_copy['left_volunteers'],
        name='减少同工',
        marker=dict(color='#d62728'),
        hovertemplate='<b>%{x}</b><br>减少同工: %{y}人<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=18)
        ),
        xaxis_title='时间',
        yaxis_title='同工人数变化',
        height=400,
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    
    return fig








def create_period_comparison_chart(df: pd.DataFrame, title: str, weeks: int) -> go.Figure:
    """创建期间环比变化条形图"""
    if df is None or df.empty:
        return go.Figure()
    
    # 取前15名变化最大的同工
    top_changes = df.head(15)
    
    # 分别处理增长和下降
    increases = top_changes[top_changes['change_amount'] >= 0]
    decreases = top_changes[top_changes['change_amount'] < 0]
    
    fig = go.Figure()
    
    # 添加增长的同工
    if not increases.empty:
        fig.add_trace(go.Bar(
            y=increases['volunteer_id'],
            x=increases['change_amount'],
            orientation='h',
            name='增长',
            marker=dict(color='#2ca02c'),
            text=increases['change_percentage'].apply(lambda x: f'+{x}%'),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>' +
                          f'最近{weeks}周: %{{customdata[0]}}次<br>' +
                          f'前{weeks}周: %{{customdata[1]}}次<br>' +
                          '变化: +%{x}次 (%{text})<br>' +
                          '<extra></extra>',
            customdata=increases[['current_services', 'previous_services']].values
        ))
    
    # 添加下降的同工
    if not decreases.empty:
        fig.add_trace(go.Bar(
            y=decreases['volunteer_id'],
            x=decreases['change_amount'],
            orientation='h',
            name='下降',
            marker=dict(color='#d62728'),
            text=decreases['change_percentage'].apply(lambda x: f'{x}%'),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>' +
                          f'最近{weeks}周: %{{customdata[0]}}次<br>' +
                          f'前{weeks}周: %{{customdata[1]}}次<br>' +
                          '变化: %{x}次 (%{text})<br>' +
                          '<extra></extra>',
            customdata=decreases[['current_services', 'previous_services']].values
        ))
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=18)
        ),
        xaxis_title='事工次数变化',
        yaxis_title='同工姓名',
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=120, r=50, t=100, b=50)
    )
    
    # 添加零线
    fig.add_vline(x=0, line=dict(color='black', width=1))
    
    return fig








# =============================================================================
# 全新桑基图：同工月际事工流动可视化
# =============================================================================

def create_volunteer_ministry_flow_sankey(df: pd.DataFrame, title: str = "同工月际事工流动") -> go.Figure:
    """
    创建同工月际事工流动桑基图
    专注显示每个同工每个月在各种事工中的流动情况
    
    参数:
    - df: 包含流动数据的DataFrame，应包含以下列:
          volunteer_name, from_month, to_month, from_ministry, to_ministry, flow_intensity
    - title: 图表标题
    """
    if df is None or df.empty:
        return go.Figure()
    
    # 创建层次化节点：月份-事工组合
    unique_nodes = set()
    for _, row in df.iterrows():
        from_node = f"{row['from_month']}\n{row['from_ministry']}"
        to_node = f"{row['to_month']}\n{row['to_ministry']}"
        unique_nodes.add(from_node)
        unique_nodes.add(to_node)
    
    node_list = sorted(list(unique_nodes))
    node_dict = {node: idx for idx, node in enumerate(node_list)}
    
    # 定义事工颜色映射
    ministry_colors = {
        '主领': '#FF6B6B',    # 红色
        '司琴': '#4ECDC4',    # 青色
        '领诗': '#45B7D1',    # 蓝色
        '音控': '#96CEB4',    # 绿色
        '录影': '#FFEAA7',    # 黄色
        '招待': '#DDA0DD',    # 紫色
        '总务': '#98D8C8',    # 薄荷绿
        '未参与': '#BDC3C7',  # 灰色
        '其他': '#F7DC6F'     # 浅黄
    }
    
    # 为节点分配颜色
    node_colors = []
    for node in node_list:
        # 提取事工名称（节点格式：月份\n事工）
        ministry = node.split('\n')[1] if '\n' in node else node
        color = ministry_colors.get(ministry, '#95A5A6')  # 默认灰色
        node_colors.append(color)
    
    # 准备连接数据
    sources = []
    targets = []
    values = []
    link_labels = []
    
    for _, row in df.iterrows():
        from_node = f"{row['from_month']}\n{row['from_ministry']}"
        to_node = f"{row['to_month']}\n{row['to_ministry']}"
        
        sources.append(node_dict[from_node])
        targets.append(node_dict[to_node])
        values.append(row['flow_intensity'])
        
        # 创建悬停信息
        label = (f"同工: {row['volunteer_name']}<br>"
                f"{row['from_ministry']} → {row['to_ministry']}<br>"
                f"时期: {row['from_month']} → {row['to_month']}<br>"
                f"流动强度: {row['flow_intensity']}")
        link_labels.append(label)
    
    # 创建桑基图
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color="black", width=1),
            label=node_list,
            color=node_colors,
            hovertemplate='<b>%{label}</b><br>总流量: %{value}<extra></extra>'
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            label=link_labels,
            color='rgba(0,0,0,0.1)',
            hovertemplate='%{label}<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=20, family="Arial, sans-serif")
        ),
        height=800,
        font=dict(size=12),
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='white'
    )
    
    return fig


def create_simplified_ministry_flow(df: pd.DataFrame, selected_volunteers: list = None) -> go.Figure:
    """
    创建简化版同工事工流动图
    可选择特定同工进行分析
    
    参数:
    - df: 原始服务数据
    - selected_volunteers: 选中的同工列表，None表示显示所有同工
    """
    if df is None or df.empty:
        return go.Figure()
    
    # 筛选同工
    if selected_volunteers:
        df = df[df['volunteer_name'].isin(selected_volunteers)]
    
    if df.empty:
        return go.Figure()
    
    # 按月份和事工聚合
    monthly_data = df.groupby(['year_month', 'ministry', 'volunteer_name']).size().reset_index(name='service_count')
    
    # 计算相邻月份的主要事工变化
    flow_data = []
    for volunteer in monthly_data['volunteer_name'].unique():
        vol_data = monthly_data[monthly_data['volunteer_name'] == volunteer].sort_values('year_month')
        
        # 确定每月的主要事工
        main_ministry_by_month = {}
        for month in vol_data['year_month'].unique():
            month_data = vol_data[vol_data['year_month'] == month]
            main_ministry = month_data.loc[month_data['service_count'].idxmax(), 'ministry']
            main_ministry_by_month[month] = main_ministry
        
        # 计算月际流动
        months = sorted(main_ministry_by_month.keys())
        for i in range(len(months) - 1):
            from_month = months[i]
            to_month = months[i + 1]
            from_ministry = main_ministry_by_month[from_month]
            to_ministry = main_ministry_by_month[to_month]
            
            flow_data.append({
                'volunteer_name': volunteer,
                'from_month': from_month.strftime('%Y-%m'),
                'to_month': to_month.strftime('%Y-%m'),
                'from_ministry': from_ministry,
                'to_ministry': to_ministry,
                'flow_intensity': 1  # 每个同工的流动强度为1
            })
    
    if not flow_data:
        return go.Figure()
    
    flow_df = pd.DataFrame(flow_data)
    return create_volunteer_ministry_flow_sankey(flow_df, "同工事工流动分析")


def display_ministry_flow_insights(df: pd.DataFrame):
    """显示事工流动分析洞察"""
    if df is None or df.empty:
        st.info("暂无流动数据")
        return
    
    st.subheader("📊 流动分析洞察")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # 总流动次数
        total_flows = len(df)
        st.metric("总流动记录", f"{total_flows:,}")
    
    with col2:
        # 参与同工数
        unique_volunteers = df['volunteer_name'].nunique()
        st.metric("参与同工数", f"{unique_volunteers}")
    
    with col3:
        # 涉及事工数
        unique_ministries = set(df['from_ministry'].unique()) | set(df['to_ministry'].unique())
        st.metric("涉及事工数", f"{len(unique_ministries)}")
    
    with col4:
        # 稳定率（同事工继续的比例）
        stable_flows = df[df['from_ministry'] == df['to_ministry']]
        stability_rate = (len(stable_flows) / total_flows * 100) if total_flows > 0 else 0
        st.metric("事工稳定率", f"{stability_rate:.1f}%")
    
    # 流动详情表格
    st.subheader("📋 流动详情")
    
    # 按事工类型分组统计
    ministry_stats = []
    for ministry in unique_ministries:
        outflow = len(df[df['from_ministry'] == ministry])
        inflow = len(df[df['to_ministry'] == ministry])
        net_flow = inflow - outflow
        
        ministry_stats.append({
            '事工': ministry,
            '流出': outflow,
            '流入': inflow,
            '净流入': net_flow
        })
    
    stats_df = pd.DataFrame(ministry_stats).sort_values('净流入', ascending=False)
    st.dataframe(stats_df, use_container_width=True, hide_index=True)


# =============================================================================
# 新增：总体概况可视化功能
# =============================================================================

def display_data_time_range(time_range_info: dict):
    """显示数据时间范围信息"""
    if not time_range_info:
        st.info("暂无时间范围数据")
        return
    
    st.subheader("📅 数据时间范围与周期")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "起始日期",
            time_range_info['start_date'].strftime('%Y-%m-%d'),
            help="数据记录的最早日期"
        )
    
    with col2:
        st.metric(
            "结束日期", 
            time_range_info['end_date'].strftime('%Y-%m-%d'),
            help="数据记录的最晚日期"
        )
    
    with col3:
        st.metric(
            "总天数", 
            f"{time_range_info['total_days']} 天",
            help="数据跨越的总天数"
        )
    
    with col4:
        st.metric(
            "总周数", 
            f"{time_range_info['total_weeks']} 周",
            help="数据跨越的总周数"
        )
    
    # 添加时间轴可视化
    fig = go.Figure()
    
    # 创建时间轴条形图
    fig.add_trace(go.Bar(
        x=[time_range_info['start_date'], time_range_info['end_date']],
        y=['数据时间范围', '数据时间范围'],
        orientation='h',
        width=0.3,
        marker=dict(color='#4CAF50'),
        showlegend=False,
        hovertemplate='<b>%{x}</b><br>总记录数: %{customdata}<extra></extra>',
        customdata=[time_range_info['total_records'], time_range_info['total_records']]
    ))
    
    fig.update_layout(
        title=dict(
            text=f"数据时间轴：共 {time_range_info['total_records']:,} 条记录",
            x=0.5,
            font=dict(size=16)
        ),
        xaxis_title='日期',
        height=200,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=80, r=20, t=60, b=40),
        yaxis=dict(showticklabels=False)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_worker_participation_overview(participation_info: dict):
    """显示同工总体参与情况KPI卡片"""
    if not participation_info:
        st.info("暂无参与情况数据")
        return
    
    st.subheader("👥 同工总体参与情况")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "同工总人数",
            f"{participation_info['total_workers']} 人",
            help="数据库中记录的所有同工数量"
        )
    
    with col2:
        st.metric(
            "活跃同工",
            f"{participation_info['active_workers']} 人",
            help="最近30天内有事工记录的同工"
        )
    
    with col3:
        st.metric(
            "未活跃同工",
            f"{participation_info['inactive_workers']} 人",
            help="最近30天内无事工记录的同工"
        )
    
    with col4:
        delta_color = "normal" if participation_info['activity_rate'] >= 50 else "inverse"
        st.metric(
            "活跃率",
            f"{participation_info['activity_rate']:.1f}%",
            help="活跃同工占总同工的比例"
        )
    
    # 添加饼图显示参与情况
    fig = go.Figure(data=[go.Pie(
        labels=['活跃同工', '未活跃同工'],
        values=[participation_info['active_workers'], participation_info['inactive_workers']],
        hole=0.4,
        marker=dict(colors=['#4CAF50', '#FF9800']),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>人数: %{value}<br>占比: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text="同工活跃情况分布",
            x=0.5,
            font=dict(size=16)
        ),
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        font=dict(size=12)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_worker_burden_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """创建同工参与负担分布箱型图和柱状图"""
    if df is None or df.empty:
        return go.Figure()
    
    # 创建子图：箱型图 + 柱状图
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('同工事工次数分布（箱型图）', 'Top 10 最活跃同工'),
        vertical_spacing=0.15,
        row_heights=[0.4, 0.6]
    )
    
    # 添加箱型图
    fig.add_trace(go.Box(
        y=df['total_services'],
        name='事工次数分布',
        marker=dict(color='#4CAF50'),
        boxpoints='outliers',
        hovertemplate='事工次数: %{y}<extra></extra>'
    ), row=1, col=1)
    
    # 添加Top 10柱状图
    top_10 = df.head(10)
    colors = ['#FFD700', '#C0C0C0', '#CD7F32'] + ['#4CAF50'] * 7  # 金银铜 + 绿色
    
    fig.add_trace(go.Bar(
        x=top_10['volunteer_id'],
        y=top_10['total_services'],
        marker=dict(color=colors[:len(top_10)]),
        text=top_10['total_services'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>事工次数: %{y}<br>服务类型数: %{customdata}<extra></extra>',
        customdata=top_10['service_types_count']
    ), row=2, col=1)
    
    fig.update_layout(
        title=dict(
            text="同工参与负担分析",
            x=0.5,
            font=dict(size=18)
        ),
        height=700,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        showlegend=False
    )
    
    # 更新x轴标签角度
    fig.update_xaxes(tickangle=45, row=2, col=1)
    
    return fig


def create_service_category_pie_chart(df: pd.DataFrame) -> go.Figure:
    """创建事工类别分布饼图"""
    if df is None or df.empty:
        return go.Figure()
    
    # 定义事工颜色
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
              '#DDA0DD', '#98D8C8', '#F7DC6F', '#95A5A6']
    
    fig = go.Figure(data=[go.Pie(
        labels=df['service_type'],
        values=df['total_services'],
        hole=0.4,
        marker=dict(colors=colors[:len(df)]),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>事工次数: %{value}<br>参与人数: %{customdata}<br>占比: %{percent}<extra></extra>',
        customdata=df['unique_volunteers']
    )])
    
    fig.update_layout(
        title=dict(
            text="事工类别分布",
            x=0.5,
            font=dict(size=18)
        ),
        height=500,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        ),
        font=dict(size=12),
        margin=dict(l=20, r=150, t=60, b=20)
    )
    
    return fig


def create_monthly_activity_heatmap(df: pd.DataFrame) -> go.Figure:
    """创建月度活动热力图"""
    if df is None or df.empty:
        return go.Figure()
    
    # 创建双轴图：事工次数 + 活跃人数
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('月度事工次数趋势', '月度活跃同工人数趋势'),
        vertical_spacing=0.15
    )
    
    # 添加事工次数趋势
    fig.add_trace(go.Scatter(
        x=df['year_month'],
        y=df['total_services'],
        mode='lines+markers',
        name='事工次数',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=8),
        fill='tonexty',
        fillcolor='rgba(255, 107, 107, 0.2)',
        hovertemplate='<b>%{x}</b><br>事工次数: %{y}<br>活跃同工: %{customdata}<extra></extra>',
        customdata=df['active_volunteers']
    ), row=1, col=1)
    
    # 添加活跃人数趋势
    fig.add_trace(go.Scatter(
        x=df['year_month'],
        y=df['active_volunteers'],
        mode='lines+markers',
        name='活跃同工',
        line=dict(color='#4ECDC4', width=3),
        marker=dict(size=8),
        fill='tonexty',
        fillcolor='rgba(78, 205, 196, 0.2)',
        hovertemplate='<b>%{x}</b><br>活跃同工: %{y}人<br>事工次数: %{customdata}<extra></extra>',
        customdata=df['total_services']
    ), row=2, col=1)
    
    fig.update_layout(
        title=dict(
            text="月度事工活动趋势与季节性分析",
            x=0.5,
            font=dict(size=18)
        ),
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        showlegend=False
    )
    
    # 更新x轴标签角度
    fig.update_xaxes(tickangle=45)
    
    return fig



