# M2 定向模式增益优化

## 实验总结

这是基于先前负向 M2 结果开展的一轮事后工程优化，不是确认性研究，也不是生物机制验证或生物到 AI 的迁移证据。

- **优点：** 两种控制器都只有 3 个可训练参数；直接按导航误差训练；10 个训练随机种子；对两个新 hazard 使用共享测试 episode；保留了等噪声和反向噪声压力条件。F/R 学习增益确实分离，说明优化器学到了模式条件化。
- **失败/不确定处：** 主差值（模式增益减通用上下文）为 `+0.000526`，交叉 95% 区间 `[-0.000395, +0.001445]` 跨零；两个主 hazard 的差值方向相反，不能认定有稳定优势。
- **经验：** 参数量匹配和直接优化主终点仍不足以保证门控结构跨环境有效；需把“单一聚合优势”与“不同环境下方向翻转”同时报告。
- **结论：** 本轮不确定，依合同停止本优化线；不根据本轮结果继续调参。

详细数值、解释边界和复核证据见 [`RESULTS.md`](RESULTS.md)。运行协议与冻结记录见 [`M2_TARGETED_GAIN_OPTIMIZATION_CONTRACT.md`](M2_TARGETED_GAIN_OPTIMIZATION_CONTRACT.md) 和 [`M2_TARGETED_GAIN_OPTIMIZATION_PREFLIGHT.json`](M2_TARGETED_GAIN_OPTIMIZATION_PREFLIGHT.json)。

## 文件位置

- 模型/运行代码：[`model/M2_TARGETED_GAIN_OPTIMIZATION/`](../../model/M2_TARGETED_GAIN_OPTIMIZATION/)
- 结果表与机器可读摘要：[`data/results/M2_TARGETED_GAIN_OPTIMIZATION/`](../../data/results/M2_TARGETED_GAIN_OPTIMIZATION/)
- 这里保存协议、优点、失败经验和结果解读。
