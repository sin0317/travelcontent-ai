## 参赛项目名称

游纪 · AI 旅行内容官（TravelContent AI）

## 团队 / 作者

sin0317（刘峻豪，个人参赛）

## 旅行场景与目标用户

- **旅行场景**：目的地行程规划 + 旅行内容创作。用户输入「目的地 + 天数」（如「开封 2 日游」），应用调用飞猪实时真实数据（景点 / 门票 / 酒店 / 机票），生成结构化行程，并进一步产出一条可直接用于抖音 / B站 / 小红书的旅行攻略口播脚本。
- **目标用户**：① 文旅 / 古城出游人群（默认以历史古迹等类别切入，适配开封、西安、杭州等文旅城市）；② 旅行短视频创作者，需要"真实数据 + 可拍脚本"的一键素材。

## 我做了什么

1. **真实数据底座**：所有行程与价格来自飞猪 Fliggy MCP 实时返回，绝不臆造；支持 `search-poi` / `search-hotel` / `search-flight` / `keyword-search` 四类查询。
2. **内容化输出（差异化亮点）**：不止给列表，而是把真实数据编排成「N 天可执行行程 + 短视频口播脚本（钩子 → 每日亮点 → CTA）」，直接对接短视频创作工作流。
3. **双形态交付**：① 阿里云百炼 Managed Agent（系统提示词驱动，开箱即用）；② 本地可跑的 Python 工程（纯标准库，零模型依赖，便于评审一键复现）。
4. **文旅契合**：默认以历史古迹等类别切入，呼应古城 / 文旅城市，已用「开封 2 日游」跑通真实样例（见 `demo/sample_output.md`）。

## 百炼使用说明（必填）

本作品以**阿里云百炼 Managed Agent 作为运行载体**：在百炼智能体中安装飞猪 Skill，由百炼大模型完成「真实数据编排 + 短视频脚本生成」。仓库内另含一套可本地复现的 Python 工程（不依赖百炼也能跑通），作为评审一键复现的兜底路径。

- 百炼能力 / 模型：百炼 Managed Agent（托管智能体）+ 通义系列大模型（百炼默认配置，可在控制台切换 qwen-max / qwen-plus 等）
- 调用方式（百炼 API / DashScope SDK / 百炼 CLI `bl` / OpenWork）：百炼 Managed Agent 控制台部署；系统提示词见仓库 `prompts/system_prompt.md`，部署步骤见 `agent/agent-config.md`
- 使用环节与输入输出：输入 = 用户自然语言（如「开封 2 日游，给我真实景点和酒店，再写一条抖音口播脚本」）→ 百炼智能体调用飞猪 Skill 拉取真实景点 / 酒店 / 机票 → 百炼大模型编排成结构化行程 + 短视频口播脚本 → 输出 = Markdown 行程卡（含图片 / 预订链接）+ 口播脚本
- Skill 名称（如有）：alibaba-flyai/flyai-skill（飞猪 Skill，提供 hotel / flight / poi / keyword 搜索能力）
- 其他工具 / 技术栈：@fly-ai/flyai-cli（Fliggy MCP 本地调用）、Python 3 本地复现工程（`src/`，纯标准库）

> ⚠️ 说明：百炼控制台部署为手动步骤（需你的百炼账号粘贴系统提示词 + 配 `FLYAI_API_KEY`），本仓库已备齐全部配置与提示词，部署后即可在百炼内直接对话产出。建议提交前补一张百炼运行截图（见下「效果展示」）。

## 效果展示

- 百炼运行截图：⚠️ 建议补充一张「在百炼 Managed Agent 中输入『开封 2 日游』并生成行程 + 脚本」的运行截图（部署步骤见 `agent/agent-config.md`）。
- 真实数据示例（本地工程产出）：见仓库 `demo/sample_output.md` —— 开封 2 日游，含清明上河园、开封城墙等 4 个真实景点（地址 + 购票链接）+ 10 家真实酒店（含价格）。
- 演示视频（强烈推荐）：⚠️ 待补充录屏。

## 项目链接与复现方式

- GitHub 仓库：https://github.com/sin0317/travelcontent-ai
- 本地复现步骤：
  1. `git clone https://github.com/sin0317/travelcontent-ai.git && cd travelcontent-ai`
  2. `npm i @fly-ai/flyai-cli`（飞猪 Skill 本地 CLI）
  3. `cp .env.example .env` 并填入 `FLYAI_API_KEY`（申请：https://flyai.open.fliggy.com/）
  4. `python src/cli.py 开封 --days 2 --category 历史古迹 --out demo/out.md` 生成行程 + 脚本
- 百炼复现步骤：见 `agent/agent-config.md`（装 flyai-skill → 贴 `prompts/system_prompt.md` → 配 `FLYAI_API_KEY` → 对话验证）。
- 注意：仓库已通过 `.gitignore` 排除 `.env`，不提交任何 API Key / 敏感信息。

## 踩坑记录（可选）

1. **百炼为必填项**：官方提交模板明确「本赛事作品必须使用阿里云百炼」。最初以为可仅用本地工程参赛，后按官方模板纠正——已把百炼 Managed Agent 作为运行载体写入提交说明，并备齐系统提示词与部署步骤。
2. **飞猪 CLI 安装**：`@fly-ai/flyai-cli` 需 Node 18+，局部安装即可；trial 模式无需 Key 可拉到少量脱敏数据，配 `FLYAI_API_KEY` 后价格完整、数据更全。
3. **密钥安全**：`FLYAI_API_KEY` 仅存本地 `.env`，已被 `.gitignore` 忽略，确认未进入 GitHub 仓库（仓库仅含 `.env.example` 模板）。
4. **推送 GitHub 走代理卡死**：本机 `http_proxy` 会让 `git push` 卡住，使用 `env HTTPS_PROXY= HTTP_PROXY= NO_PROXY=140.82.112.3,github.com git push` 绕过直连成功。
