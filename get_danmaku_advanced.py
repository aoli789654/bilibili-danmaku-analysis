import requests
import json
import xml.etree.ElementTree as ET
import time
import csv
import re

def parse_bilibili_url(url_string):
    if not url_string: return None
    ep_match = re.search(r'ep(?:_id=)?([0-9]+)', url_string)
    if ep_match: return {'type': 'epid', 'value': ep_match.group(1)}
    bv_match = re.search(r'(BV[1-9A-HJ-NP-Za-km-z]+)', url_string, re.IGNORECASE)
    if bv_match: return {'type': 'bvid', 'value': bv_match.group(1)}
    av_match = re.search(r'av([0-9]+)', url_string, re.IGNORECASE)
    if av_match: return {'type': 'avid', 'value': av_match.group(1)}
    ss_match = re.search(r'ss(?:eason_id=)?([0-9]+)', url_string)
    if ss_match: return {'type': 'ssid', 'value': ss_match.group(1)}
    print(f"未能从URL '{url_string}' 中识别出有效的B站ID模式。")
    return None

def fetch_cid(parsed_info):
    if not parsed_info: return None
    identifier_type, identifier_value = parsed_info['type'], parsed_info['value']
    common_headers = {'User-Agent': 'Mozilla/5.0...', 'Accept': 'application/json...'}
    try:
        if identifier_type in ['bvid', 'avid']:
            api_url = "https://api.bilibili.com/x/player/pagelist?"
            params = {'bvid': identifier_value} if identifier_type == 'bvid' else {'aid': identifier_value}
            response = requests.get(api_url, params=params, headers=common_headers, timeout=10)
            data = response.json()
            if data.get('code') == 0 and data.get('data'):
                cid = data['data'][0].get('cid')
                if cid: print(f"成功获取CID: {cid}"); return cid
        elif identifier_type in ['epid', 'ssid']:
            api_url = f"https://api.bilibili.com/pgc/view/web/season?"
            params = {'ep_id': identifier_value} if identifier_type == 'epid' else {'season_id': identifier_value}
            response = requests.get(api_url, params=params, headers=common_headers, timeout=10)
            data = response.json()
            if data.get('code') == 0 and data.get('result') and data['result'].get('episodes'):
                cid = data['result']['episodes'][0].get('cid')
                if cid: print(f"成功获取CID: {cid}"); return cid
    except Exception as e:
        print(f"获取CID时出错: {e}")
    return None

def get_danmaku_xml_by_cid(cid):
    if not cid: return None
    url = f"https://comment.bilibili.com/{cid}.xml"
    headers = {'User-Agent': 'Mozilla/5.0...', 'Accept': 'application/xml...'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.content.decode('utf-8', 'ignore')
    except Exception as e:
        print(f"请求弹幕XML时发生网络错误: {e}")
    return None

def parse_danmaku_from_xml(xml_data):
    if not xml_data: return []
    try:
        root = ET.fromstring(xml_data)
        danmaku_data = []
        for d_element in root.findall('d'):
            if d_element.text:
                p_attribute = d_element.get('p')
                if p_attribute:
                    timestamp = float(p_attribute.split(',')[0])
                    text = d_element.text.strip()
                    danmaku_data.append({'timestamp': timestamp, 'text': text})
        print(f"成功解析到 {len(danmaku_data)} 条弹幕（包含时间戳）。")
        return danmaku_data
    except ET.ParseError as e:
        print(f"解析弹幕XML时出错: {e}")
        return []

def save_danmaku_to_csv(danmaku_data, filename="danmaku.csv"):
    if not danmaku_data:
        print("弹幕列表为空，不创建CSV文件。")
        return
    try:
        print(f"正在将 {len(danmaku_data)} 条弹幕保存到 {filename}...")
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            # 定义表头为 'timestamp' 和 'text'
            writer = csv.DictWriter(csvfile, fieldnames=['timestamp', 'text'])
            writer.writeheader()
            writer.writerows(danmaku_data)
        print(f"成功保存到 {filename}")
    except IOError as e:
        print(f"保存弹幕到CSV文件时发生IO错误: {e}")

if __name__ == "__main__":
    target_url = input("请输入B站视频或番剧的URL: ")
    output_csv_filename = "danmaku.csv"
    print(f"===== 开始处理B站弹幕获取任务: {target_url} =====")
    parsed_info = parse_bilibili_url(target_url)
    if parsed_info:
        video_cid = fetch_cid(parsed_info)
        if video_cid:
            danmaku_xml = get_danmaku_xml_by_cid(video_cid)
            if danmaku_xml:
                danmaku_list = parse_danmaku_from_xml(danmaku_xml)
                if danmaku_list:
                    save_danmaku_to_csv(danmaku_list, output_csv_filename)
    print(f"\n===== 任务处理完毕 =====")