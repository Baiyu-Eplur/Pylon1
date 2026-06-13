# 架空线缆 galloping 模型异常响应问题与修正方案阶段总结

日期：2026-06-13

## 1. 问题背景

本项目目标是建立能够真实模拟架空线缆 galloping 机理的 OpenSees 时域模型，而不是仅仅得到一个可收敛的结构动力响应。研究对象为 typical 工况：

- 跨距 `L = 322.8 m`
- 垂度 `H = 10.48 m`
- 风场强度 `u_star = 0.6`
- 时间步 `dt = 0.05 s`
- 本次验证时长 `72 s`

早期模型在约 `69-70 s` 附近出现异常大响应。该响应最初看起来像强 galloping，但进一步检查发现，它不能直接作为物理驰振结论，因为模型中仍存在若干流程和建模问题。

## 2. 旧方案的主要问题

旧方案存在四类问题：

1. 气动阻尼主要作为判据或后处理指标记录，未必真实进入 OpenSees 时域动力方程。
2. 旧的显式负阻尼力可能把 Den Hartog 判据人工放大为速度方向上的持续正反馈。
3. 原结构单元可能出现非物理负张力或压缩状态，不符合架空线缆“只能拉、不能压”的基本特征。
4. 初始重力和平衡流程没有被严格验证。旧的 assumed-equilibrium 路径中，重力可能没有作为正确的自重平衡状态进入动力阶段。

其中第 4 点最终被确认是异常大响应问题被关闭的直接关键。

## 3. 四项关键修改

### 3.1 阻尼参与方式修改

旧流程可以计算负气动阻尼指标，但该指标不一定真正影响 OpenSees 动力方程。现在 Rayleigh 阻尼保留为结构基本阻尼，气动阻尼指标保留为诊断量，真实气动反馈通过实时气动力分支进入 OpenSees 时域方程。

### 3.2 气动力施加方式修改

采用增量准定常气动力：

```text
F_total = F_original + [F_current - F_reference]
```

其中 `F_original` 是原始 Path 风荷载，`F_reference` 是参考线形和参考风速下的准定常力，`F_current` 是每个 OpenSees 时间步根据当前节点速度、局部变形方向、相对风速和攻角重新计算的准定常 drag/lift。该修改避免重复计入基准风荷载，也避免将 Den Hartog 判据人工写成必然正反馈。

### 3.3 单元形式修改

采用 tension-only 模型：

```text
corotTruss + ElasticPPGap + InitStrainMaterial
```

并修正关键单位问题：

```text
ElasticPPGap Fy 是材料应力，不是轴向力
Fy = rated_strength_N / Area
```

该修改保证线缆保持“只能拉、不能压”的物理特征。本次最终验证中，slack element count 全程为 `0`。

### 3.4 重力与初始平衡流程修改

旧 assumed-equilibrium 方案没有完成真实静力平衡便进入动力阶段。控制验证显示，旧流程中 gravity-on 和 gravity-off 的结果几乎相同，说明重力没有正确成为动力初始状态的一部分。

此外，C4 静力路线暴露了 Tcl 变量污染问题：

- `Wind_velocity_reader.tcl` 原本把风/力时间向量存入全局变量 `time`；
- C4 静力加载循环也使用 `time` 作为静力步计数变量；
- 静力阶段将风时程向量覆盖为标量，导致动力气动力插值失败。

修正后使用 C4 路线：先静力 ramp gravity，收敛后 `loadConst -time 0.0`，再进入动力分析；同时新增受保护变量 `wind_time_vector`，所有气动插值均优先使用该变量。

这是最终关闭异常响应问题的决定性修改。

## 4. 根因判断

当前结论是：

```text
异常大响应的直接核心触发，是旧流程没有可靠建立初始重力/预张力平衡，并且 C4 路线暴露出 Tcl time 变量污染风时程的问题。
```

因此：

```text
第四项是异常大响应消失的直接原因；
前三项是让模型具备科学可信度的必要条件。
```

## 5. 最终验证结果

最终使用 C4 静力平衡路线重新运行 typical galloping 工况，OpenSees 成功运行至目标时间：

```text
STATUS success
MESSAGE target_time_reached
TIME 72.0
ANALYZE_RETURN_CODE 0
```

主要结果：

- 最大位移约 `1.789 m`
- 最大速度约 `2.117 m/s`
- 最大加速度约 `74.29 m/s^2`
- 最大反力/张力尺度约 `21.34 kN`
- 最小估计张力约 `18.69 kN`
- 最大估计张力约 `21.00 kN`
- 最大单元应变约 `2.73e-5`
- slack element count 全程为 `0`

气动力诊断：

- `F_original` 约 `345.8-527.0 N`
- `F_current` 约 `352.5-548.0 N`
- `total_abs_delta_force` 约 `35.3-135.7 N`
- `max(total_abs_delta_force / F_original)` 约 `0.3045`
- 气动系数表未发生 clipping

## 6. 附带 OpenSees 工程文件

最终可直接运行的 OpenSees 工程包：

```text
teacher_c4_opensees_project/
```

运行方式：

```powershell
powershell -ExecutionPolicy Bypass -File .\run_opensees.ps1
```

附件包已从自身目录实际复测，控制台输出：

```text
ANALYSIS_STATUS success
ANALYSIS_MESSAGE target_time_reached
ANALYZE_RETURN_CODE 0
```
