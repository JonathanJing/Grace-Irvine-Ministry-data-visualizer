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


def create_weekly_trend_chart(df: pd.DataFrame, title: str) -> go.Figure:
    """创建每周事工趋势图"""
    if df is None or df.empty:
        return go.Figure()
    
    # 按周聚合数据
    weekly_summary = df.groupby('week_label').agg({
        'services_count': 'sum',
        'volunteer_id': 'nunique'
    }).reset_index()
    
    # 创建子图
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('每周总事工次数', '每周参与同工人数'),
        vertical_spacing=0.15
    )
    
    # 添加总事工次数线图
    fig.add_trace(go.Scatter(
        x=weekly_summary['week_label'],
        y=weekly_summary['services_count'],
        mode='lines+markers',
        name='总事工次数',
        line=dict(color='#2E86AB', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>总事工次数: %{y}<extra></extra>'
    ), row=1, col=1)
    
    # 添加参与人数线图
    fig.add_trace(go.Scatter(
        x=weekly_summary['week_label'],
        y=weekly_summary['volunteer_id'],
        mode='lines+markers',
        name='参与人数',
        line=dict(color='#A23B72', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>参与人数: %{y}<extra></extra>'
    ), row=2, col=1)
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=18)
        ),
        height=600,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    
    # 更新x轴标签角度
    fig.update_xaxes(tickangle=45)
    
    return fig


def create_volunteer_heatmap(df: pd.DataFrame, title: str) -> go.Figure:
    """创建同工活跃度热力图"""
    if df is None or df.empty:
        return go.Figure()
    
    # 创建透视表
    pivot_data = df.pivot_table(
        index='volunteer_id',
        columns='week_label',
        values='services_count',
        fill_value=0
    )
    
    # 只显示前20名最活跃的同工
    top_volunteers = df.groupby('volunteer_id')['services_count'].sum().nlargest(20).index
    pivot_data = pivot_data.loc[pivot_data.index.isin(top_volunteers)]
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='YlOrRd',
        hovertemplate='<b>%{y}</b><br>' +
                      '周期: %{x}<br>' +
                      '事工次数: %{z}<br>' +
                      '<extra></extra>',
        colorbar=dict(title="事工次数")
    ))
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=18)
        ),
        xaxis_title='周期',
        yaxis_title='同工姓名',
        height=600,
        font=dict(size=10)
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
