# 百炼 Managed Agent 配置说明（游纪 · AI 旅行内容官）

本作品的核心运行环境是**阿里云百炼 Managed Agent**。下面把参赛指南第 1–6 步落到本作品的具体操作。

## 第 1 步：进入百炼并选择 Managed Agent

- 打开 https://bailian.console.aliyun.com → 模型广场 → 选择 **Managed Agent**。
- 新建一个智能体，先用默认配置。

## 第 2 步：安装飞猪 Skill

在智能体会话中执行：

```
npx skills add alibaba-flyai/flyai-skill
```

安装后，智能体即可调用飞猪的酒店 / 机票 / 景点 / 度假等搜索能力。

## 第 3 步：配置系统提示词

把本仓库 `prompts/system_prompt.md` 的完整内容，粘贴为智能体的**系统提示词**。
它定义了：何时调用飞猪 Skill、真实数据卡片的展示规则、以及"短视频口播脚本"这一差异化输出。

## 第 4 步：配置环境变量（飞猪 API Key）

在百炼会话的环境变量中配置：

```
FLYAI_API_KEY=你的APIKey
```

- 申请地址：https://flyai.open.fliggy.com/
- 访客总额度 300 次；注册用户累计 5000 次，用完后每日补充 100 次。
- 更多额度：加入大赛交流群 @管理员申请。

> 不配置 Key 也能以 trial 模式体验（数据量较少，价格脱敏）。

## 第 5 步：验证核心路径

发起测试对话，例如：

```
帮我规划开封 2 日游，给我真实景点和酒店，再写一条抖音口播脚本。
```

确认飞猪 Skill 正常返回真实数据、行程与脚本正确生成。

## 第 6 步：提交作品

- 把本仓库（travelcontent-ai）推送到你的 GitHub。
- 前往大赛报名专区提交 Issue：
  https://github.com/modelstudioai/modelstudioai.github.io/issues/new?template=fliggy-ai-travel-innovation-2026.md
- 提交内容：仓库链接 + 作品简介（场景 + 核心亮点）+ 演示视频 / 截图（强烈推荐）。
- 提交模板见本仓库 `SUBMISSION.md`。
