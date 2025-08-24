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


def create_individual_volunteer_trends_chart(df: pd.DataFrame, title: str) -> go.Figure:
    """创建个人事工次数趋势折线图"""
    if df is None or df.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    # 为每个同工添加一条趋势线
    volunteers = df['volunteer_id'].unique()
    colors = px.colors.qualitative.Set3
    
    for i, volunteer in enumerate(volunteers):
        volunteer_data = df[df['volunteer_id'] == volunteer].sort_values('week_start')
        color = colors[i % len(colors)]
        
        fig.add_trace(go.Scatter(
            x=volunteer_data['week_label'],
            y=volunteer_data['services_count'],
            mode='lines+markers',
            name=volunteer,
            line=dict(color=color, width=2),
            marker=dict(size=6),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                          '周期: %{x}<br>' +
                          '事工次数: %{y}<br>' +
                          '<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=18)
        ),
        xaxis_title='周期',
        yaxis_title='事工次数',
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
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


def create_participation_distribution_chart(df: pd.DataFrame, title: str) -> go.Figure:
    """创建参与次数分布直方图"""
    if df is None or df.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['range_label'],
        y=df['volunteer_count'],
        marker=dict(color='#9467bd'),
        text=df['volunteer_count'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>' +
                      '同工人数: %{y}人<br>' +
                      '平均事工次数: %{customdata}<br>' +
                      '<extra></extra>',
        customdata=df['avg_services_in_range']
    ))
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=18)
        ),
        xaxis_title='事工次数范围',
        yaxis_title='同工人数',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        showlegend=False
    )
    
    return fig


def create_service_boxplot(df: pd.DataFrame, title: str) -> go.Figure:
    """创建同工事工次数箱型图"""
    if df is None or df.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    fig.add_trace(go.Box(
        y=df['service_count'],
        name='事工次数分布',
        marker=dict(color='#17becf'),
        boxpoints='outliers',
        hovertemplate='<b>事工次数统计</b><br>' +
                      '值: %{y}<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=18)
        ),
        yaxis_title='事工次数',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        showlegend=False
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


def create_volunteer_service_network(df: pd.DataFrame, title: str) -> go.Figure:
    """创建同工-服务类型网络图"""
    if df is None or df.empty:
        return go.Figure()
    
    # 创建网络图
    G = nx.Graph()
    
    # 添加节点和边
    for _, row in df.iterrows():
        volunteer = f"👤 {row['volunteer_id']}"
        service = f"🎯 {row['service_type_id']}"
        weight = row['collaboration_count']
        
        G.add_node(volunteer, node_type='volunteer')
        G.add_node(service, node_type='service')
        G.add_edge(volunteer, service, weight=weight)
    
    # 使用spring layout
    pos = nx.spring_layout(G, k=1, iterations=50)
    
    # 准备绘图数据
    edge_trace = []
    node_trace_volunteer = []
    node_trace_service = []
    
    # 添加边
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        weight = G[edge[0]][edge[1]]['weight']
        
        edge_trace.append(go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(width=min(weight * 2, 10), color='rgba(125,125,125,0.5)'),
            hoverinfo='none',
            showlegend=False
        ))
    
    # 添加同工节点
    for node in G.nodes():
        if G.nodes[node]['node_type'] == 'volunteer':
            x, y = pos[node]
            node_trace_volunteer.append(go.Scatter(
                x=[x],
                y=[y],
                mode='markers+text',
                marker=dict(size=20, color='#1f77b4'),
                text=[node.replace('👤 ', '')],
                textposition='bottom center',
                hovertemplate='<b>%{text}</b><br>同工<extra></extra>',
                showlegend=False
            ))
    
    # 添加服务类型节点
    for node in G.nodes():
        if G.nodes[node]['node_type'] == 'service':
            x, y = pos[node]
            node_trace_service.append(go.Scatter(
                x=[x],
                y=[y],
                mode='markers+text',
                marker=dict(size=15, color='#ff7f0e', symbol='square'),
                text=[node.replace('🎯 ', '')],
                textposition='top center',
                hovertemplate='<b>%{text}</b><br>服务类型<extra></extra>',
                showlegend=False
            ))
    
    # 创建图形
    fig = go.Figure()
    
    # 添加所有轨迹
    for trace in edge_trace:
        fig.add_trace(trace)
    for trace in node_trace_volunteer:
        fig.add_trace(trace)
    for trace in node_trace_service:
        fig.add_trace(trace)
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=18)
        ),
        height=600,
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=10)
    )
    
    return fig


def display_advanced_insights(df_stats: pd.DataFrame, df_distribution: pd.DataFrame):
    """显示高级数据洞察"""
    st.subheader("📊 深度数据洞察")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if df_stats is not None and not df_stats.empty:
            median_services = df_stats['service_count'].median()
            st.metric(
                "中位数事工次数",
                f"{median_services:.0f} 次",
                ""
            )
        else:
            st.metric("中位数事工次数", "暂无数据", "")
    
    with col2:
        if df_stats is not None and not df_stats.empty:
            q1 = df_stats['service_count'].quantile(0.25)
            q3 = df_stats['service_count'].quantile(0.75)
            iqr = q3 - q1
            st.metric(
                "四分位距",
                f"{iqr:.1f}",
                f"Q1: {q1:.1f}, Q3: {q3:.1f}"
            )
        else:
            st.metric("四分位距", "暂无数据", "")
    
    with col3:
        if df_distribution is not None and not df_distribution.empty:
            most_common = df_distribution.loc[df_distribution['volunteer_count'].idxmax(), 'range_label']
            most_common_count = df_distribution['volunteer_count'].max()
            st.metric(
                "最常见参与度",
                most_common,
                f"{most_common_count} 人"
            )
        else:
            st.metric("最常见参与度", "暂无数据", "")
    
    with col4:
        if df_stats is not None and not df_stats.empty:
            high_performers = (df_stats['service_count'] > df_stats['service_count'].quantile(0.9)).sum()
            st.metric(
                "高频参与者",
                f"{high_performers} 人",
                f"(前10%)"
            )


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



