#!/usr/bin/env python3
"""
Labubu 数据采集脚本
查询近 30 天数据并保存为 data.json
用法: python3 fetch.py
"""

import json
import os
import ssl
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

API_KEY  = os.environ.get("REDASH_API_KEY", "iCrDraVFVBNduschd1ghPb1sOu3R0EpTP4r4YuEz")
QUERY_ID = 2309
BASE     = "https://dp.echo.tech"
ctx      = ssl.create_default_context()


def post(start, end, max_age):
    data = json.dumps({
        "parameters": {"date_picker": {"start": start, "end": end}},
        "max_age": max_age,
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/api/queries/{QUERY_ID}/results",
        data=data, method="POST",
        headers={
            "Authorization": f"Key {API_KEY}",
            "Content-Type":  "application/json",
        },
    )
    with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
        return json.loads(r.read())


def fetch_data():
    end_dt   = datetime.now()
    start_dt = end_dt - timedelta(days=29)
    start_str = start_dt.strftime("%Y-%m-%d")
    end_str   = end_dt.strftime("%Y-%m-%d")

    print(f"📅 查询范围: {start_str} → {end_str}")

    # 触发查询
    r = post(start_str, end_str, 0)
    if "query_result" in r:
        rows = r["query_result"]["data"]["rows"]
        print(f"✅ 直接返回 {len(rows)} 行")
        return rows, start_str, end_str

    # 异步 job，轮询
    for i in range(60):
        time.sleep(3)
        print(f"   等待服务端... ({i + 1}/60)")
        r = post(start_str, end_str, 300)
        if "query_result" in r:
            rows = r["query_result"]["data"]["rows"]
            print(f"✅ 获取到 {len(rows)} 行")
            return rows, start_str, end_str
        status = r.get("job", {}).get("status")
        if status in (4, 5):
            raise RuntimeError(r["job"].get("error", "查询失败"))

    raise TimeoutError("轮询超时，请重试")


if __name__ == "__main__":
    rows, start_str, end_str = fetch_data()

    output = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "date_start": start_str,
        "date_end":   end_str,
        "row_count":  len(rows),
        "rows":       rows,
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, separators=(",", ":"))

    print(f"💾 data.json 已保存（{len(rows)} 行，约 {len(json.dumps(output)) // 1024} KB）")
