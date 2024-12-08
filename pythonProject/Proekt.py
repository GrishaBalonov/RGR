import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Загрузка данных
df = pd.read_csv('financial_data.csv')
df['date'] = pd.to_datetime(df['date'])

# Создание Dash приложения
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Финансовый Аналитический Дашборд", style={'text-align': 'center', 'color': '#2C3E50'}),
    html.Div([
        html.P("Этот дашборд предоставляет комплексный анализ финансовых данных, "
               "включая доходы, расходы и прибыль. Вы можете выбрать период анализа (месяц, квартал или год) "
               "и визуально отслеживать свои финансовые потоки.",
               style={'text-align': 'center', 'font-size': '18px'})
    ]),

    dcc.Dropdown(
        id='period-dropdown',
        options=[
            {'label': 'Месяц', 'value': 'month'},
            {'label': 'Квартал', 'value': 'quarter'},
            {'label': 'Год', 'value': 'year'},
        ],
        value='month',
        style={'width': '50%', 'margin': 'auto', 'padding': '10px'}
    ),

    html.Div([
        dcc.Graph(id='income-expenses-line-chart'),
        dcc.Graph(id='expenses-category-pie-chart'),
        dcc.Graph(id='profit-distribution-histogram'),
        dcc.Graph(id='profit-scatter-plot'),
        html.Div(id='financial-indicators', style={'text-align': 'center', 'font-size': '20px', 'margin-top': '20px'})
    ], style={'padding': '20px'}),

], style={'backgroundColor': '#ECF0F1', 'padding': '20px'})


@app.callback(
    Output('income-expenses-line-chart', 'figure'),
    Output('expenses-category-pie-chart', 'figure'),
    Output('profit-distribution-histogram', 'figure'),
    Output('profit-scatter-plot', 'figure'),
    Output('financial-indicators', 'children'),
    Input('period-dropdown', 'value')
)
def update_dash(period):
    # Группировка данных по выбранному периоду
    global grouped_data
    if period == 'month':
        grouped_data = df.groupby(pd.Grouper(key='date', freq='M')).sum().reset_index()
    elif period == 'quarter':
        grouped_data = df.groupby(pd.Grouper(key='date', freq='Q')).sum().reset_index()
    elif period == 'year':
        grouped_data = df.groupby(pd.Grouper(key='date', freq='Y')).sum().reset_index()

    # Расчет прибыли
    grouped_data['profit'] = grouped_data['income'] - grouped_data['expenses']

    # Динамика доходов и расходов
    income_expenses_fig = px.line(grouped_data, x='date', y=['income', 'expenses'], title='Динамика доходов и расходов')
    income_expenses_fig.update_layout(paper_bgcolor='lightblue', title_font=dict(size=24))

    # Обновление названий
    income_expenses_fig.for_each_trace(
        lambda t: t.update(name=t.name.replace('income', 'Доходы').replace('expenses', 'Расходы')))
    income_expenses_fig.update_layout(legend_title_text='Тип значений', xaxis_title='Дата', yaxis_title='Значение')

    # Структура расходов по категориям
    expenses_categories = df.groupby(pd.Grouper(key='date', freq='M'))['expenses'].sum().reset_index()
    expenses_pie_fig = px.pie(expenses_categories, names='date', values='expenses',
                              title='Структура расходов по категориям')

    # Анализ распределения прибыли
    profit_hist_fig = px.histogram(grouped_data, x='profit', title='Распределение прибыли')
    profit_hist_fig.update_layout(paper_bgcolor='lightcoral', title_font=dict(size=24))
    profit_hist_fig.update_layout(xaxis_title='Прибыль', yaxis_title='Количество')

    # Анализ корреляции между прибылью и расходами
    scatter_fig = go.Figure()
    scatter_fig.add_trace(go.Scatter(x=grouped_data['expenses'], y=grouped_data['profit'],
                                     mode='markers', name='Данные', marker=dict(color='blue')))

    # Расчет линии регрессии
    scatter_fig.add_trace(go.Scatter(x=grouped_data['expenses'], y=grouped_data['profit'].rolling(window=3).mean(),
                                     mode='lines', name='Линия регрессии', line=dict(color='red', width=2)))

    scatter_fig.update_layout(title='Анализ корреляции между прибылью и расходами',
                              xaxis_title='Расходы', yaxis_title='Прибыль',
                              paper_bgcolor='lightyellow', title_font=dict(size=24))

    # Финансовые показатели
    total_income = grouped_data['income'].sum()
    total_expenses = grouped_data['expenses'].sum()
    total_profit = total_income - total_expenses
    indicators = f'Прибыль: {total_profit}, Выручка: {total_income}, Расходы: {total_expenses}'

    return income_expenses_fig, expenses_pie_fig, profit_hist_fig, scatter_fig, indicators


if __name__ == '__main__':
    app.run_server(debug=True)