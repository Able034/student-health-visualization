import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Output, Input

# 读取数据
df = pd.read_excel('Student Smoking, Alcohol, and Mental Health Data(1)(1).xlsx')
df.columns = df.columns.str.strip()  # 清理列名空格

# 心理健康的顺序定义
health_order = ['优秀', '好', '平均', '低于平均水平', '差']

# 初始化 Dash 应用
app = Dash(__name__)
app.title = "学生心理健康分析"

# 页面布局
app.layout = html.Div([
    html.H1("学生吸烟、饮酒与心理健康数据分析"),
    dcc.Dropdown(
        id='question-dropdown',
        options=[
            {'label': '1. 吸烟、酒精和心理健康之间相互作用（桑基图）', 'value': 'q1'},
            {'label': '2. 研究领域对于吸烟、喝酒的作用（堆叠条形图）', 'value': 'q2'},
            {'label': '3. 年龄与吸烟、喝酒的关系（箱线图）', 'value': 'q3'},
            {'label': '4. 吸烟与饮酒之间是否有联系（热力图）', 'value': 'q4'},
        ],
        value='q1',
        clearable=False,
        style={'width': '60%', 'margin': '20px auto'}
    ),
    dcc.Graph(id='graph-output', style={'height': '700px'})
])

# 回调函数
@app.callback(
    Output('graph-output', 'figure'),
    Input('question-dropdown', 'value')
)
def update_graph(selected_q):
    if selected_q == 'q1':
        # 桑基图
        labels = []
        smoke_labels = df['吸烟频率'].dropna().unique().tolist()
        alcohol_labels = df['酒精消费频率'].dropna().unique().tolist()
        health_labels = health_order

        labels.extend(smoke_labels)
        labels.extend(alcohol_labels)
        labels.extend(health_labels)

        smoke_idx = {k: i for i, k in enumerate(smoke_labels)}
        alcohol_idx = {k: i + len(smoke_labels) for i, k in enumerate(alcohol_labels)}
        health_idx = {k: i + len(smoke_labels) + len(alcohol_labels) for i, k in enumerate(health_labels)}

        source, target, value = [], [], []

        for s in smoke_labels:
            sub_df = df[df['吸烟频率'] == s]
            counts = sub_df['酒精消费频率'].value_counts()
            for a, v in counts.items():
                if pd.isna(a): continue
                source.append(smoke_idx[s])
                target.append(alcohol_idx[a])
                value.append(v)

        for a in alcohol_labels:
            sub_df = df[df['酒精消费频率'] == a]
            counts = sub_df['心理健康'].value_counts()
            for h, v in counts.items():
                if pd.isna(h) or h not in health_idx: continue
                source.append(alcohol_idx[a])
                target.append(health_idx[h])
                value.append(v)

        fig = go.Figure(go.Sankey(
            node=dict(label=labels, pad=15, thickness=20),
            link=dict(source=source, target=target, value=value)
        ))
        fig.update_layout(title="吸烟、饮酒与心理健康关系（桑基图）", font_size=12)
        return fig

    elif selected_q == 'q2':
        # 研究领域 vs 吸烟频率（堆叠条形图）
        smoke_ct = pd.crosstab(df['研究领域'], df['吸烟频率'])
        fig = px.bar(smoke_ct, title='不同研究领域的吸烟频率分布',
                     labels={'index': '研究领域', 'value': '人数', 'variable': '吸烟频率'},
                     barmode='stack',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        return fig

    elif selected_q == 'q3':
        # 年龄 vs 吸烟频率（箱线图）
        fig = px.box(df, x='吸烟频率', y='年龄', color='吸烟频率',
                     title='不同吸烟频率对应的年龄分布',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        return fig

    elif selected_q == 'q4':
        # 热力图：吸烟 vs 酒精
        heat = pd.crosstab(df['吸烟频率'], df['酒精消费频率'])
        fig = px.imshow(heat,
                        labels=dict(x='酒精消费频率', y='吸烟频率', color='人数'),
                        title='吸烟频率与酒精消费频率的关系热力图',
                        color_continuous_scale='Viridis')
        return fig

# 启动服务器
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=False, host='0.0.0.0', port=port)
