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


def create_service_type_pie_chart(df: pd.DataFrame, title: str) -> go.Figure:
    """创建服务类型分布饼图"""
    if df is None or df.empty:
        return go.Figure()
    
    fig = go.Figure(data=[go.Pie(
        labels=df['service_type_id'],
        values=df['total_services'],
        hole=0.4,
        hovertemplate='<b>%{label}</b><br>' +
                      '事工次数: %{value}<br>' +
                      '占比: %{percent}<br>' +
                      '参与人数: %{customdata}<br>' +
                      '<extra></extra>',
        customdata=df['unique_volunteers'],
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig.update_layout(
        title=dict(
            text=title,
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
            x=1.05
        ),
        font=dict(size=12)
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
# 桑基图可视化功能
# =============================================================================

def create_service_transition_sankey(df: pd.DataFrame, title: str) -> go.Figure:
    """创建事工类型转换桑基图"""
    if df is None or df.empty:
        return go.Figure()
    
    # 准备桑基图数据
    all_services = list(set(df['from_service'].unique().tolist() + df['to_service'].unique().tolist()))
    
    # 创建节点索引映射
    node_dict = {service: idx for idx, service in enumerate(all_services)}
    
    # 准备节点
    node_labels = all_services
    node_colors = [f'rgba({hash(service) % 255}, {(hash(service) * 2) % 255}, {(hash(service) * 3) % 255}, 0.8)' 
                   for service in all_services]
    
    # 准备连接
    sources = [node_dict[row['from_service']] for _, row in df.iterrows()]
    targets = [node_dict[row['to_service']] for _, row in df.iterrows()]
    values = df['transition_count'].tolist()
    
    # 为连接添加悬停信息
    link_labels = [f"{row['from_service']} → {row['to_service']}<br>"
                   f"转换次数: {row['transition_count']}<br>"
                   f"涉及同工: {row['volunteer_count']}人<br>"
                   f"同工列表: {row['volunteers'][:100]}..." 
                   if len(row['volunteers']) > 100 else row['volunteers']
                   for _, row in df.iterrows()]
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            label=link_labels,
            hovertemplate='%{label}<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=18)
        ),
        height=600,
        font=dict(size=12)
    )
    
    return fig


def create_volunteer_journey_sankey(df: pd.DataFrame, title: str) -> go.Figure:
    """创建同工参与度演变桑基图"""
    if df is None or df.empty:
        return go.Figure()
    
    # 准备桑基图数据
    all_levels = list(set(df['from_level'].unique().tolist() + df['to_level'].unique().tolist()))
    
    # 定义参与度级别的颜色
    level_colors = {
        '未参与': 'rgba(128, 128, 128, 0.8)',
        '低参与度': 'rgba(255, 99, 132, 0.8)',
        '中参与度': 'rgba(255, 205, 86, 0.8)',
        '高参与度': 'rgba(75, 192, 192, 0.8)',
        '超高参与度': 'rgba(54, 162, 235, 0.8)'
    }
    
    # 创建节点索引映射
    node_dict = {level: idx for idx, level in enumerate(all_levels)}
    
    # 准备节点
    node_labels = all_levels
    node_colors = [level_colors.get(level, 'rgba(128, 128, 128, 0.8)') for level in all_levels]
    
    # 准备连接
    sources = [node_dict[row['from_level']] for _, row in df.iterrows()]
    targets = [node_dict[row['to_level']] for _, row in df.iterrows()]
    values = df['transition_count'].tolist()
    
    # 为连接添加悬停信息
    link_labels = [f"{row['from_level']} → {row['to_level']}<br>"
                   f"转换次数: {row['transition_count']}<br>"
                   f"涉及同工: {row['volunteer_count']}人"
                   for _, row in df.iterrows()]
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            label=link_labels,
            hovertemplate='%{label}<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=18)
        ),
        height=600,
        font=dict(size=12)
    )
    
    return fig


def create_seasonal_flow_sankey(df: pd.DataFrame, title: str) -> go.Figure:
    """创建季节性事工流动桑基图"""
    if df is None or df.empty:
        return go.Figure()
    
    # 准备桑基图数据
    all_nodes = list(set(df['source'].unique().tolist() + df['target'].unique().tolist()))
    
    # 创建节点索引映射
    node_dict = {node: idx for idx, node in enumerate(all_nodes)}
    
    # 准备节点颜色（季节性颜色）
    def get_node_color(node_name):
        if '第一季度' in node_name:
            return 'rgba(144, 238, 144, 0.8)'  # 浅绿色 - 春天
        elif '第二季度' in node_name:
            return 'rgba(255, 182, 193, 0.8)'  # 浅粉色 - 夏天
        elif '第三季度' in node_name:
            return 'rgba(255, 165, 0, 0.8)'    # 橙色 - 秋天
        elif '第四季度' in node_name:
            return 'rgba(173, 216, 230, 0.8)'  # 浅蓝色 - 冬天
        else:
            return 'rgba(128, 128, 128, 0.8)'  # 灰色 - 其他
    
    # 准备节点
    node_labels = all_nodes
    node_colors = [get_node_color(node) for node in all_nodes]
    
    # 准备连接
    sources = [node_dict[row['source']] for _, row in df.iterrows()]
    targets = [node_dict[row['target']] for _, row in df.iterrows()]
    values = df['flow_count'].tolist()
    
    # 为连接添加悬停信息
    link_labels = [f"{row['source']}<br>↓<br>{row['target']}<br>"
                   f"流动次数: {row['flow_count']}<br>"
                   f"涉及同工: {row['volunteer_count']}人"
                   for _, row in df.iterrows()]
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            label=link_labels,
            hovertemplate='%{label}<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=18)
        ),
        height=700,
        font=dict(size=12)
    )
    
    return fig


def create_experience_progression_sankey(df: pd.DataFrame, title: str) -> go.Figure:
    """创建同工经验进阶桑基图"""
    if df is None or df.empty:
        return go.Figure()
    
    # 准备桑基图数据
    all_categories = list(set(df['source'].unique().tolist() + df['target'].unique().tolist()))
    
    # 定义类型和贡献级别的颜色
    category_colors = {
        # 同工类型颜色
        '专精型': 'rgba(255, 99, 132, 0.8)',
        '双技能型': 'rgba(54, 162, 235, 0.8)',
        '多才型': 'rgba(75, 192, 192, 0.8)',
        # 贡献级别颜色
        '初级贡献': 'rgba(255, 205, 86, 0.8)',
        '中级贡献': 'rgba(153, 102, 255, 0.8)',
        '高级贡献': 'rgba(255, 159, 64, 0.8)',
        '顶级贡献': 'rgba(199, 199, 199, 0.8)'
    }
    
    # 创建节点索引映射
    node_dict = {category: idx for idx, category in enumerate(all_categories)}
    
    # 准备节点
    node_labels = all_categories
    node_colors = [category_colors.get(category, 'rgba(128, 128, 128, 0.8)') for category in all_categories]
    
    # 准备连接
    sources = [node_dict[row['source']] for _, row in df.iterrows()]
    targets = [node_dict[row['target']] for _, row in df.iterrows()]
    values = df['volunteer_count'].tolist()
    
    # 为连接添加悬停信息
    link_labels = [f"{row['source']} → {row['target']}<br>"
                   f"同工人数: {row['volunteer_count']}<br>"
                   f"平均技能数: {row['avg_skills']}"
                   for _, row in df.iterrows()]
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            label=link_labels,
            hovertemplate='%{label}<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=18)
        ),
        height=600,
        font=dict(size=12)
    )
    
    return fig


def display_sankey_insights(
    transitions_df: pd.DataFrame, 
    journey_df: pd.DataFrame, 
    seasonal_df: pd.DataFrame, 
    experience_df: pd.DataFrame
):
    """显示桑基图分析洞察"""
    st.subheader("📊 流动模式洞察")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if transitions_df is not None and not transitions_df.empty:
            most_common_transition = transitions_df.iloc[0]
            st.metric(
                "最常见转换",
                f"{most_common_transition['from_service']} → {most_common_transition['to_service']}",
                f"{most_common_transition['transition_count']} 次"
            )
        else:
            st.metric("最常见转换", "暂无数据", "")
    
    with col2:
        if journey_df is not None and not journey_df.empty:
            most_common_journey = journey_df.iloc[0]
            st.metric(
                "最常见参与度变化",
                f"{most_common_journey['from_level']} → {most_common_journey['to_level']}",
                f"{most_common_journey['transition_count']} 次"
            )
        else:
            st.metric("最常见参与度变化", "暂无数据", "")
    
    with col3:
        if seasonal_df is not None and not seasonal_df.empty:
            most_common_seasonal = seasonal_df.iloc[0]
            st.metric(
                "最活跃季节流动",
                "季节性转换",
                f"{most_common_seasonal['flow_count']} 次"
            )
        else:
            st.metric("最活跃季节流动", "暂无数据", "")
    
    with col4:
        if experience_df is not None and not experience_df.empty:
            most_common_progression = experience_df.iloc[0]
            st.metric(
                "最常见进阶路径",
                f"{most_common_progression['source']} → {most_common_progression['target']}",
                f"{most_common_progression['volunteer_count']} 人"
            )
