# Cable Analyser

## 项目说明

本项目是对 TIMUR4/ 目录下 MATLAB 代码的 Python 重构。
功能：模拟 overhead cable 在风荷载（含气动力与 galloping 负阻尼效应）下的动力响应。
核心流程：几何建模 → OpenSees TCL 生成 → 求解器调用 → 后处理。

---

## 与原 MATLAB 版本的对应关系

| Python 模块 | 原 MATLAB 文件 |
|---|---|
| geometry.py | CABLE_ANALYSER_Updating.m（几何段）|
| tcl_writer.py（write_modal） | MODAL.m |
| tcl_writer.py（write_time_history）| TH_Constant.m |
| postprocess.py | CABLE_ANALYSER_Updating.m（后处理段）|
| analysis.py | CABLE_ANALYSER_Updating.m（主流程）|

---

## 未迁移的 MATLAB 文件（保留在 TIMUR4/ 中）

- `Figure.m` / `figurefordamp.m`：可视化脚本，暂不迁移
- `KaimalModel.m` / `cohDavenport.m`：风场生成函数，当前分析不调用
- `get_CABLE_Geometry.m` / `get_TH_Para.m`：辅助函数，参数已内联

---

## 安装

```bash
pip install -r requirements.txt
```

---

## 使用方法

```bash
# 默认配置运行时程分析
python main.py

# 指定配置文件和分析类型
python main.py --config config/default_config.yaml --analysis-type MODAL

# 指定 OpenSees 路径
python main.py --opensees-path "D:/path/to/opensees.bat"
```

---

## 配置文件说明

修改 `config/default_config.yaml` 中的参数后直接运行，无需改动代码。

关键参数：

| 参数 | 说明 |
|---|---|
| `solver.opensees_path` | **必须修改**为实际的 OpenSees 可执行文件路径 |
| `time_history.folder_1` | 荷载工况列表，对应 `data/forces/` 下的一级子目录 |
| `time_history.folder_2` | 模拟批次列表，对应 `data/forces/FORCE_x/` 下的二级子目录 |
| `geometry.type` | 1 = 抛物线，2 = 悬链线，3 = 折线（V 形） |
| `material.ro` | 缆线密度（kg/m³），用于计算 `self_weight = Area × ro × g` |
| `damping.model` | `Rayleigh`（质量比例）或 `Modal` |

---

## 目录结构

```
cable_analyser/
├── config/
│   └── default_config.yaml      # 所有可调参数
├── src/
│   └── cable_analyser/
│       ├── geometry.py          # 几何生成、截面属性、节点质量
│       ├── tcl_writer.py        # OpenSees Tcl 文件生成
│       ├── solver.py            # OpenSees 可执行文件调用
│       ├── postprocess.py       # 结果读取与后处理
│       └── analysis.py          # 主流程编排
├── tcl_procedures/              # 手写 Tcl 过程文件（不可修改）
├── data/
│   ├── forces/                  # 气动荷载时程（FORCE_x/SIMx/NODE_*.txt）
│   ├── wind/SIM1/               # 风速时程（Wind_velocity_reader.tcl 的读取源）
│   └── aero_coeffs/             # 气动系数表（CD、CL、dCL）
├── output/                      # OpenSees 输出文件（运行时生成）
├── tests/                       # pytest 测试套件
├── main.py                      # 命令行入口
└── requirements.txt
```

---

## 运行测试

```bash
cd cable_analyser
pytest tests/ -v
```

---

## 注意事项

- `self_weight` 由 `Area * ro * g` 计算，不硬编码（与 TIMUR4/CABLE_ANALYSER_Updating.m 中的 `15.9 N/m` 不同，后者使用了等效密度假设）
- `tcl_procedures/` 中的 `.tcl` 文件不可修改（自定义求解过程和阻尼更新逻辑）
- TIMUR4/ 原始文件完整保留，本项目独立建立，两者互不干扰
- 执行 TH 分析前 OpenSees 必须先完成 MODAL 运行，以生成 `output/modal_simple.out`（`analysis.py` 已自动处理此依赖顺序）
