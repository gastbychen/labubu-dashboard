# Labubu 价格行情看板

基于 Redash API 的 Labubu 潮玩市场价格数据可视化平台，支持实时查询各款式均价走势、成交量与同比涨跌。

**在线访问：** https://redash-api-doc.vercel.app

---

## 功能特性

- **日期范围筛选** — 默认近 14 天，支持自定义起止日期
- **交易类型切换** — C2C / EXCHANGE 独立展示
- **款式搜索** — 按名称关键词实时过滤
- **卡片视图** — 每款 SPU 一张卡片，含三日均价折线图
- **列表视图** — 单行紧凑布局，支持多列排序
- **排序** — 默认按 3 日成交量降序，支持按均价、同比、成交量等字段切换
- **折叠超量卡片** — 超过 200 款后自动折叠，按需展开
- **详情弹窗** — 点击任意卡片 / 列表行，展示该款式全部 API 字段
- **概览统计** — 总款式数、最高涨幅、最大跌幅、数据时间范围

---

## 数据说明

| 字段 | 说明 |
|---|---|
| `avg_price_3days` | 近 3 日均价（卡片大字展示，折线图数据源） |
| `avg_price_3days_yoy` | 近 3 日均价同比（API 预算，红涨绿跌） |
| `trading_volume_3days` | 近 3 日成交量（默认排序依据） |
| `avg_price_30days` | 近 30 日均价 |
| `avg_price_365days` | 近 365 日均价 |
| `trading_volume_Xdays` | 各周期成交量（1 / 3 / 30 / 365 / 全历史） |
| `product_quantity_Xdays` | 各周期上架量 |

> **成交量环比**：`(最新日 - 前一日) / 前一日 × 100%`，由前端计算（API 未提供 `trading_volume_3days_yoy`）

---

## 技术栈

| 层次 | 技术 |
|---|---|
| 前端 | 单文件 HTML + Vanilla JS + CSS Variables |
| 图表 | [Chart.js 4](https://www.chartjs.org/) via CDN |
| 字体 | Bebas Neue · JetBrains Mono · Inter via Google Fonts |
| 代理 | Vercel Serverless Function（解决 CORS） |
| 部署 | [Vercel](https://vercel.com) |

---

## 项目结构

```
├── labubu-dashboard.html   # 主页面（全部前端逻辑）
├── api/
│   └── [...path].js        # Vercel 反向代理（转发至 dp.echo.tech）
├── server.py               # 本地开发代理服务器
├── vercel.json             # Vercel 路由配置
├── package.json            # Node.js 版本声明
└── README.md
```

---

## 本地开发

无需 Node.js 构建，直接运行本地代理服务器：

```bash
# 启动代理（端口 8080）
python3 server.py

# 浏览器访问
open http://localhost:8080/labubu-dashboard.html
```

> 直接双击打开 HTML 文件会因 CORS 限制导致 `Failed to fetch`，必须通过代理访问。

---

## 部署更新

每次修改 `labubu-dashboard.html` 后，执行一条命令发布：

```bash
vercel --prod
```

---

## API 接口

| 项目 | 内容 |
|---|---|
| Endpoint | `POST https://dp.echo.tech/api/queries/2309/results` |
| 认证 | `Authorization: Key <api_key>` |
| 参数 | `date_picker.start` / `date_picker.end`（YYYY-MM-DD） |

**轮询机制：** 接口首次返回 `job` 对象时，需以 `max_age=300` 重复 POST 直至返回 `query_result`（`/api/jobs/{id}` 在该实例上不可用）。

```bash
# 示例调用
curl -X POST "https://dp.echo.tech/api/queries/2309/results" \
  -H "Authorization: Key iCrDraVFVBNduschd1ghPb1sOu3R0EpTP4r4YuEz" \
  -H "Content-Type: application/json" \
  -d '{"parameters":{"date_picker":{"start":"2026-02-12","end":"2026-02-26"}},"max_age":0}'
```
