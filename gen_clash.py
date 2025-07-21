import requests
import re
import yaml

README_URL = "https://raw.githubusercontent.com/TopChina/proxy-list/main/README.md"
TEMPLATE_PATH = "iKuuu_V2.yaml"
CLASH_OUT = "clash.yaml"

def fetch_readme():
    return requests.get(README_URL).text

def parse_proxies(md):
    proxies = []
    country_flag = lambda c: {
        "中国": "🇨🇳", "香港": "🇭🇰", "台湾": "🇨🇳", "日本": "🇯🇵", "新加坡": "🇸🇬", "美国": "🇺🇲", "英国": "🇬🇧"
        # 可自行扩充
    }.get(c, "")
    for line in md.splitlines():
        match = re.match(r'\| ([\d\.]+):(\d+) \| ([^\|]+) \| ([^\|]+) \|', line)
        if match:
            ip, port, country, username = match.groups()
            name = f"{country_flag(country)}{country}_{ip}:{port}"
            proxies.append({
                "name": name,
                "type": "http",
                "server": ip,
                "port": int(port),
                "username": username,
                "password": "1",
                "udp": True
            })
    return proxies

def load_template():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def update_yaml(template, proxies):
    template['proxies'] = proxies
    proxy_names = [p['name'] for p in proxies]
    for group in template.get('proxy-groups', []):
        # 只保留 DIRECT/REJECT/分组引用等特殊值
        group['proxies'] = proxy_names + [x for x in group.get('proxies', []) if x in ['DIRECT', 'REJECT']]
    return template

def save_yaml(data):
    with open(CLASH_OUT, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True)

if __name__ == "__main__":
    md = fetch_readme()
    proxies = parse_proxies(md)
    template = load_template()
    result = update_yaml(template, proxies)
    save_yaml(result)
