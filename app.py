import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Output, Input

# 读取数据（调整文件路径）
df = pd.read_excel('Student Smoking, Alcohol, and Mental Health Data(1)(1).xlsx')
df.columns = df.columns.str.strip()

# 心理健康排序，方便堆叠条形图统一顺序
health_order = ['优秀', '好', '平均', '低于平均水平', '差']

app = Dash(__name__)

app.layout = html.Div([
    html.H1("学生吸烟、饮酒与心理健康数据分析"),
    
    dcc.Dropdown(
        id='question-dropdown',
        options=[
            {'label': '1. 吸烟、酒精和心理健康之间相互作用', 'value': 'q1'},
            {'label': '2. 研究领域对于吸烟、喝酒的作用', 'value': 'q2'},
            {'label': '3. 年龄与吸烟、喝酒的关系', 'value': 'q3'},
            {'label': '4. 吸烟与饮酒之间是否有联系', 'value': 'q5'},  # 原q5改为q4编号
        ],
        value='q1',
        clearable=False,
        style={'width': '60%'}
    ),
    dcc.Graph(id='graph-output', style={'height': '700px'}),
])

@app.callback(
    Output('graph-output', 'figure'),
    Input('question-dropdown', 'value')
)
def update_graph(selected_q):
    if selected_q == 'q1':
        # 1. 吸烟、酒精和心理健康之间相互作用 - 桑基图
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
        
        links_source = []
        links_target = []
        links_value = []
        
        for s in smoke_labels:
            sub_df = df[df['吸烟频率'] == s]
            counts = sub_df['酒精消费频率'].value_counts()
            for a, v in counts.items():
                if pd.isna(a): 
                    continue
                links_source.append(smoke_idx[s])
                links_target.append(alcohol_idx[a])
                links_value.append(v)
        
        for a in alcohol_labels:
            sub_df = df[df['酒精消费频率'] == a]
            counts = sub_df['心理健康'].value_counts()
            for h, v in counts.items():
                if pd.isna(h):
                    continue
                if h not in health_idx:
                    continue
                links_source.append(alcohol_idx[a])
                links_target.append(health_idx[h])
                links_value.append(v)
        
        fig = go.Figure(go.Sankey(
            node=dict(label=labels, pad=15, thickness=20, color="lightblue"),
            link=dict(source=links_source, target=links_target, value=links_value)
        ))
        fig.update_layout(title_text="吸烟、饮酒与心理健康关系（桑基图）", font_size=12)
        return fig

    elif selected_q == 'q2':
        # 2. 研究领域对吸烟喝酒的作用 - 分组堆叠条形图
        smoke_ct = pd.crosstab(df['研究领域'], df['吸烟频率'])
        alcohol_ct = pd.crosstab(df['研究领域'], df['酒精消费频率'])
        
        fig_smoke = px.bar(
            smoke_ct,
            labels={'index': '研究领域', 'value': '人数', 'variable': '吸烟频率'},
            title='不同研究领域吸烟频率分布',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            barmode='stack'
        )
        
        # 这里只返回吸烟分布图，可扩展为tabs选择
        return fig_smoke
    
    elif selected_q == 'q3':
        # 3. 年龄与吸烟喝酒的关系 - 箱线图
        fig_smoke = px.box(df, x='吸烟频率', y='年龄', color='吸烟频率',
                           title='不同吸烟频率对应年龄分布', 
                           color_discrete_sequence=px.colors.qualitative.Pastel)
        return fig_smoke
    
    else:  # q4: 吸烟与饮酒之间是否有联系 - 热力图
        heat = pd.crosstab(df['吸烟频率'], df['酒精消费频率'])
        fig = px.imshow(heat,
                        labels=dict(x='酒精消费频率', y='吸烟频率', color='人数'),
                        color_continuous_scale='Viridis',
                        title='吸烟频率与酒精消费频率交叉热力图')
        return fig


if __name__ == '__main__':
    app.run(debug=True)
