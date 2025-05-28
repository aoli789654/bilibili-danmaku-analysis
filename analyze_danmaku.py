# analyze_danmaku.py (一键生成报告版 V3.0 - 含全部图表)

import pandas as pd
from transformers import pipeline
import jieba_fast.analyse
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
from wordcloud import WordCloud  # 确保WordCloud已导入

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
pd.set_option('display.max_columns', None)

def extract_key_info(dataframe):
    """提取核心关键词并返回列表"""
    print("模块A: 正在提取核心关键词...")
    text_all = " ".join(dataframe['text'].astype(str))
    keywords = jieba_fast.analyse.textrank(text_all, topK=20, withWeight=False)
    return keywords


def find_memes(dataframe):
    """发现高频短语/梗并返回字典"""
    print("模块B: 正在发现社区热梗...")
    all_texts = dataframe['text'].astype(str).tolist()

    def generate_ngrams(text_list, n):
        ngrams = []
        for text in text_list:
            words = [word for word in jieba_fast.cut(text) if len(word) > 1]
            for i in range(len(words) - n + 1):
                ngrams.append("".join(words[i:i + n]))
        return ngrams

    results = {}
    for n in [2, 3]:
        ngrams_list = generate_ngrams(all_texts, n)
        if ngrams_list:
            results[f'Top 10 高频{n}字短语'] = Counter(ngrams_list).most_common(10)
    return results

def time_series_analysis(dataframe, output_filename='danmaku_timeseries_plot.png'):
    """进行时间序列分析，保存图表并返回图表文件名和高能时刻信息"""
    print("模块C: 正在进行时间序列分析...")
    # ... (这部分函数内部代码与之前相同，保持不变)
    bin_size = 10
    bins = np.arange(0, dataframe['timestamp'].max() + bin_size, bin_size)
    density, _ = np.histogram(dataframe['timestamp'], bins=bins)
    fig, ax = plt.subplots(figsize=(15, 7))
    ax.plot(bins[:-1], density, color='dodgerblue', label='弹幕密度 (条/10秒)')
    ax.set_title('视频弹幕密度与高能时刻分析', fontsize=16)
    ax.grid(True, linestyle='--', alpha=0.6)
    high_energy_moments = []
    if len(density) > 0:
        top_3_indices = density.argsort()[-3:][::-1]
        for i, index in enumerate(top_3_indices):
            start_time, end_time, count = int(bins[index]), int(bins[index + 1]), int(density[index])
            high_energy_moments.append(f"Top {i + 1}: 在 {start_time}-{end_time} 秒期间, 爆发了 {count} 条弹幕。")
            ax.axvline(x=bins[index], color='red', linestyle='--', alpha=0.8)
            ax.text(bins[index], count, f' Top {i + 1}\n{count}条', color='red')
    ax.legend()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"时间序列图已保存为 {output_filename}")
    return output_filename, high_energy_moments

def sentiment_analysis(dataframe):
    """对DataFrame进行情感分析并返回带有情感标签的DataFrame"""
    print("模块D: 正在进行情感分析...")
    sentiment_pipeline = pipeline('sentiment-analysis', model='uer/roberta-base-finetuned-dianping-chinese')
    danmaku_texts = dataframe['text'].astype(str).tolist()
    sentiment_results = sentiment_pipeline(danmaku_texts)
    dataframe['sentiment_label'] = [result['label'] for result in sentiment_results]
    dataframe['sentiment_score'] = [result['score'] for result in sentiment_results]
    print("情感分析完成。")
    return dataframe

def generate_sentiment_pie_chart(dataframe, output_filename='danmaku_sentiment_pie_chart.png'):
    """根据情感分析结果生成饼图并保存"""
    print("模块E: 正在生成情感分布饼图...")
    sentiment_counts = dataframe['sentiment_label'].value_counts()
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=140,
           textprops={'fontsize': 14}, colors=['lightcoral', 'lightskyblue'])
    ax.set_title('弹幕情感分布分析', fontsize=16)
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"情感分布饼图已保存为 {output_filename}")
    return output_filename

def generate_word_cloud(dataframe, output_filename='danmaku_wordcloud.png'):
    """根据文本内容生成词云图并保存"""
    print("模块F: 正在生成词云图...")
    text_all = " ".join(dataframe['text'].astype(str))
    stopwords = {'的', '了', '是', '我', '在', '也', '啊', '吗', '哈'}  # 自定义停用词
    filtered_words = [word for word in jieba_fast.cut(text_all) if word not in stopwords and len(word) > 1]
    text_segmented = " ".join(filtered_words)

    wordcloud = WordCloud(
        font_path='C:/Windows/Fonts/simhei.ttf',
        background_color='white',
        width=1000,
        height=700,
        collocations=False
    ).generate(text_segmented)
    wordcloud.to_file(output_filename)
    print(f"词云图已保存为 {output_filename}")
    return output_filename

def generate_html_report(summary_data, timeseries_plot_filename, sentiment_pie_chart_filename, word_cloud_filename):
    """生成一体化的HTML分析报告"""
    print("模块G: 正在生成最终的HTML分析报告...")

    keywords_html = f"<li>{'</li><li>'.join(summary_data['keywords'])}</li>"
    memes_html = ""
    for title, meme_list in summary_data['memes'].items():
        memes_html += f"<h4>{title}</h4><ul>"
        for phrase, count in meme_list: memes_html += f"<li>'{phrase}' - 出现了 {count} 次</li>"
        memes_html += "</ul>"
    moments_html = f"<li>{'</li><li>'.join(summary_data['high_energy_moments'])}</li>"
    data_table_html = summary_data['dataframe'].to_html(classes='dataframe', index=False, escape=False)

    html_template = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>B站弹幕深度分析报告</title>
        <style>
            body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 20px; background-color: #f4f4f9; }}
            h1, h2, h3 {{ color: #333; border-bottom: 2px solid #4a90e2; padding-bottom: 10px;}}
            .container {{ max-width: 1200px; margin: auto; background-color: #fff; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); border-radius: 8px; }}
            .section {{ padding: 20px; margin-bottom: 20px; border-radius: 8px; }}
            .flex-container {{ display: flex; flex-wrap: wrap; gap: 20px; align-items: flex-start; }}
            .flex-item {{ flex: 1; min-width: 400px; }}
            .dataframe {{ border-collapse: collapse; width: 100%; }}
            .dataframe th, .dataframe td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            .dataframe th {{ background-color: #4a90e2; color: white; }}
            img {{ max-width: 100%; height: auto; display: block; margin: 20px auto; border: 1px solid #ddd; border-radius: 4px;}}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>B站弹幕深度分析报告</h1>
            <div class="section">
                <h2>一、观众情绪与互动热点概览</h2>
                <div class="flex-container">
                    <div class="flex-item">
                        <h3>情感分布概览</h3>
                        <img src="{sentiment_pie_chart_filename}" alt="弹幕情感分布饼图">
                    </div>
                    <div class="flex-item">
                        <h3>高能时刻Top 3总结</h3>
                        <p>通过弹幕密度分析，我们定位到观众互动最热烈的时刻：</p>
                        <ul>{moments_html}</ul>
                    </div>
                </div>
            </div>
            <div class="section">
                <h2>二、核心话题分析</h2>
                <div class="flex-container">
                    <div class="flex-item">
                        <h3>观众讨论词云</h3>
                        <img src="{word_cloud_filename}" alt="弹幕讨论词云图">
                    </div>
                    <div class="flex-item">
                        <h3>核心关键词 (Top 20)</h3>
                        <ul>{keywords_html}</ul>
                        <h3>社区热梗发现</h3>
                        {memes_html}
                    </div>
                </div>
            </div>
            <div class="section">
                <h2>三、高能时刻详情分析</h2>
                <img src="{timeseries_plot_filename}" alt="弹幕时间序列分析图">
            </div>
            <div class="section">
                <h2>四、弹幕数据详情（含情感分析）</h2>
                {data_table_html}
            </div>
        </div>
    </body>
    </html>
    """
    report_filename = "Bilibili_Danmaku_Analysis_Report.html"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"HTML报告已成功生成：{report_filename}")

if __name__ == "__main__":
    try:
        df_raw = pd.read_csv('danmaku.csv')
        df_raw.dropna(subset=['text'], inplace=True)
    except FileNotFoundError:
        print("错误：未找到 danmaku.csv。请先运行get_danmaku_advanced.py获取数据。")
        exit()

    sample_size = min(len(df_raw), 1000)
    df_analysis = df_raw.sample(n=sample_size, random_state=42).copy()
    print(f"数据加载成功！将对 {sample_size} 条随机样本进行全面分析。")
    df_with_sentiment = sentiment_analysis(df_analysis)
    keywords_result = extract_key_info(df_with_sentiment)
    memes_result = find_memes(df_with_sentiment)
    timeseries_plot_file, moments_result = time_series_analysis(df_with_sentiment)
    sentiment_pie_chart_file = generate_sentiment_pie_chart(df_with_sentiment)
    word_cloud_file = generate_word_cloud(df_with_sentiment)  # 新增

    # 整合所有结果
    summary = {
        'keywords': keywords_result,
        'memes': memes_result,
        'high_energy_moments': moments_result,
        'dataframe': df_with_sentiment
    }
    # 生成最终报告，传入全部三个图表的文件名
    generate_html_report(summary, timeseries_plot_file, sentiment_pie_chart_file, word_cloud_file)
    # 保存Excel文件
    excel_filename = "danmaku_analysis_results.xlsx"
    df_with_sentiment.to_excel(excel_filename, index=False, engine='openpyxl')
    print(f"详细数据也已保存到Excel文件：{excel_filename}")

    print("\n所有任务已圆满完成！自动化报告已包含全部三种图表，请打开HTML文件查看最终成果")