# 原始需求

为 ai-daily-brief 项目新增飞书（Lark）Webhook 机器人推送功能。

## 用户需求

- 每日简报以交互卡片形式推送到飞书群
- 生成（08:00 北京时间）和推送（10:00 北京时间）解耦
- 不修改现有 pipeline 代码
- Fork 友好：fork 用户只需设 1 个 Secret 即可启用

## 约束

- 使用飞书自定义机器人 Webhook（无需应用审批）
- 推送前校验日期，避免推送过期内容
- Webhook URL 缺失时 exit 0（不影响 fork 用户 CI）
