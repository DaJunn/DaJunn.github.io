# Agent Html馆

Agent 生成的单文件 HTML 网页都住这里，`index.html` 是自动生成的总目录（带搜索）。

## 日常用法

- **新增页面**：把 `.html` 丢进本文件夹 → `python3 build_index.py` 重新生成目录 → 找 Agent 推送上线。
- **本地打开**：直接双击 `index.html`，点卡片进入各页面。
- **线上地址**：https://dajunn.github.io/ （本仓库，推送 main 分支后约 1 分钟自动上线）

## 公开规则（重要）

本仓库公开（GitHub 免费版 Pages 的前提），`.gitignore` 里的内容**只留在本地、不上线**：

- `mcn_model.html` —— 含真实公司经营数据（GMV、达人昵称、佣金率）
- `life_sim/` —— 含真实家庭财务底牌（人生推演台全套）

新页面如果也含敏感数据，文件名加进 `.gitignore` 即可，索引里会自动标 🔒 私藏不上线。

## 文件清单

| 内容 | 说明 |
|---|---|
| `index.html` | 总目录（自动生成，勿手改） |
| `build_index.py` | 目录生成器：`python3 build_index.py` |
| `business_*.html` | 经营学习系列（单位经济学 / 现金流 / 增长） |
| `local_vs_global_optimum.html` | 思维模型演示 |
| `life_sim/`（私藏） | 人生推演台 + 三版草稿 + 引擎 |
