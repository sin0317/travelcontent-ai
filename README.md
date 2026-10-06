# 游纪 · AI 旅行内容官（TravelContent AI）

> 2026 飞猪 AI 旅行创新大赛参赛作品
> 基于飞猪真实旅行数据，输入目的地 + 天数，一键生成「可执行行程 + 可拍成短视频的旅行攻略口播脚本」。

## 一句话定位

不止于"查数据"——把飞猪实时真实数据编排成**内容**：结构化行程 + 短视频口播脚本，直接服务文旅短视频创作与传播。

## 参赛信息

- 主办方：飞猪 × 阿里云百炼
- 大赛官网：https://opc.aliyun.com/feizhu
- 提交入口：https://github.com/modelstudioai/modelstudioai.github.io/issues/new?template=fliggy-ai-travel-innovation-2026.md

## 核心亮点（差异化）

1. **真实数据底座**：所有景点 / 酒店 / 机票均来自飞猪实时返回（Fliggy MCP），绝不臆造。
2. **内容化输出**：把数据编排成 N 天行程 + 抖音 / B站风格口播脚本，区别于"只给列表"的常规旅行助手。
3. **双形态交付**：既有可本地运行验证的工程代码（Python + flyai-cli），也提供百炼 Managed Agent 系统提示词，可直接在百炼平台复现。
4. **文旅场景契合**：默认以"历史古迹"等类别切入，天然适配古城 / 文旅城市（如开封、西安、杭州），呼应 AIGC 文旅短片创作。

## 技术栈

- 数据层：飞猪 Skill（`@fly-ai/flyai-cli` → Fliggy MCP），命令输出单行 JSON
- 编排层：Python（标准库，零第三方依赖）
- 智能层：阿里云百炼 Managed Agent + 大模型（系统提示词见 `prompts/system_prompt.md`）
- 展示层：Markdown 行程卡片 + 短视频脚本

## 本地复现（无需百炼也能跑通核心路径）

```bash
# 1. 安装飞猪 CLI（本仓库已局部安装；如需重装：）
npm i @fly-ai/flyai-cli

# 2.（可选）配置 Key 以获得完整数据
cp .env.example .env
# 编辑 .env 填入 FLYAI_API_KEY（留空则走 trial 模式）

# 3. 运行（示例：开封 2 日游）
python src/cli.py 开封 --days 2 --category 历史古迹 --out demo/sample_output.md
```

- 真实示例输出见 `demo/sample_output.md`（开封 2 日游：4 个景点含真实地址与购票链接 + 9 家酒店含价格）。
- trial 模式价格脱敏（如 ¥2xx）；填入真实 Key 后价格完整显示。

## 百炼平台部署

详见 `agent/agent-config.md`：安装 `flyai-skill` → 粘贴系统提示词 → 配置 `FLYAI_API_KEY` → 验证 → 提交 Issue。

## 目录结构

```
travelcontent-ai/
├── src/
│   ├── flyai_client.py   # 飞猪 CLI 封装（调用 + JSON 解析）
│   ├── planner.py        # 行程编排（景点轮转分配到各天）
│   ├── content_gen.py    # 短视频口播脚本生成
│   └── cli.py            # 命令行入口
├── prompts/
│   └── system_prompt.md  # 百炼 Agent 系统提示词
├── agent/
│   └── agent-config.md   # 百炼智能体配置说明
├── demo/
│   └── sample_output.md  # 真实数据示例（开封 2 日游）
├── .env.example
├── SUBMISSION.md         # 提交 Issue 模板
└── README.md
```

## 作品延展

- 接入百炼大模型后，脚本可由模板升级为个性化 AI 生成；
- 结合 AIGC 视频工具（即梦 / 可灵 / Pr / Ae），可把"行程 + 脚本"进一步生成实拍混剪短视频，形成"数据 → 脚本 → 视频"的内容生产闭环。

## 许可

MIT（参赛作品，遵循大赛参赛须知中的原创与授权条款）。
