from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "reports" / "meeting_2026_06_10"
DOCX_PATH = OUT / "Galloping_Meeting_Report_CN_2026_06_10.docx"
FIG_DIR = OUT / "figures"
PKG = ROOT / "output" / "time_step_coverage_audit" / "L300_350_400_ustar_grid_n4096_s3_plus_extra" / "result_package"
SP = ROOT / "output" / "single_point_demo" / "L322P8_U0P600_SEED20260909"
VAL = ROOT / "output" / "workflow_validation"


BLUE = RGBColor(31, 77, 120)
ACCENT = RGBColor(46, 116, 181)
GREEN = RGBColor(74, 143, 90)
AMBER = RGBColor(196, 131, 43)
RED = RGBColor(178, 74, 74)
TEXT = RGBColor(32, 36, 42)
MUTED = RGBColor(95, 103, 115)
HEADER_FILL = "EAF3F8"
LIGHT_FILL = "F6F8FB"
WARN_FILL = "FFF4DE"
BORDER = "B7C9DD"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def pct(v: str | float) -> str:
    return f"{100 * float(v):.1f}%"


def font(run, size: float | None = None, bold: bool | None = None, color: RGBColor | None = None) -> None:
    run.font.name = "Calibri"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = color


def style_doc(doc: Document) -> None:
    sec = doc.sections[0]
    sec.page_width = Inches(8.5)
    sec.page_height = Inches(11)
    sec.top_margin = Inches(0.75)
    sec.bottom_margin = Inches(0.75)
    sec.left_margin = Inches(0.8)
    sec.right_margin = Inches(0.8)
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Calibri"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = TEXT
    normal.paragraph_format.line_spacing = 1.12
    normal.paragraph_format.space_after = Pt(5)
    for name, size, color, before, after in [
        ("Heading 1", 16, BLUE, 14, 7),
        ("Heading 2", 13, ACCENT, 11, 5),
        ("Heading 3", 11.5, BLUE, 8, 4),
    ]:
        st = styles[name]
        st.font.name = "Calibri"
        st._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
        st.font.size = Pt(size)
        st.font.color.rgb = color
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(after)
    header = sec.header.paragraphs[0]
    header.text = "架空导线 galloping 研究汇报材料 | 2026-06-10"
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for r in header.runs:
        font(r, 8, color=MUTED)
    footer = sec.footer.paragraphs[0]
    footer.text = "pylon1 simulation workflow | internal meeting report"
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in footer.runs:
        font(r, 8, color=MUTED)


def shade(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def borders(table, color: str = BORDER) -> None:
    tbl_pr = table._tbl.tblPr
    tbl_borders = tbl_pr.first_child_found_in("w:tblBorders")
    if tbl_borders is None:
        tbl_borders = OxmlElement("w:tblBorders")
        tbl_pr.append(tbl_borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = tbl_borders.find(qn(f"w:{edge}"))
        if el is None:
            el = OxmlElement(f"w:{edge}")
            tbl_borders.append(el)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "6")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)


def para(doc: Document, text: str, *, bold_prefix: str | None = None) -> None:
    p = doc.add_paragraph()
    if bold_prefix and text.startswith(bold_prefix):
        r = p.add_run(bold_prefix)
        font(r, bold=True, color=BLUE)
        r2 = p.add_run(text[len(bold_prefix):])
        font(r2)
    else:
        r = p.add_run(text)
        font(r)


def bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        r = p.add_run(item)
        font(r)


def numbered(doc: Document, items: list[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Number")
        r = p.add_run(item)
        font(r)


def callout(doc: Document, title: str, body: str, fill: str = HEADER_FILL) -> None:
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    borders(t, "D9E2F3")
    c = t.cell(0, 0)
    shade(c, fill)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(title)
    font(r, 10.5, True, BLUE)
    p2 = c.add_paragraph()
    p2.paragraph_format.space_after = Pt(0)
    r2 = p2.add_run(body)
    font(r2, 9.5)


def simple_table(doc: Document, headers: list[str], rows: list[list[str]], font_size: float = 8.4) -> None:
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = True
    borders(t)
    for i, h in enumerate(headers):
        cell = t.rows[0].cells[i]
        shade(cell, HEADER_FILL)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        font(r, font_size, True, BLUE)
    for row in rows:
        cells = t.add_row().cells
        for i, value in enumerate(row):
            cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(value)
            font(r, font_size)


def picture(doc: Document, path: Path, caption: str, width: float = 6.75) -> None:
    if not path.exists():
        callout(doc, "Missing figure", str(path), WARN_FILL)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Inches(width))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run(caption)
    font(r, 8.5, color=MUTED)
    r.italic = True


def make_workflow_figure() -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / "code_workflow_cn.png"
    font_path = Path("C:/Windows/Fonts/msyh.ttc")
    font_prop = font_manager.FontProperties(fname=str(font_path)) if font_path.exists() else None
    fig, ax = plt.subplots(figsize=(12.8, 5.2), dpi=180)
    ax.axis("off")
    labels = [
        ("配置层", "YAML\nL/H, material\nu_star, seed"),
        ("几何层", "CableGeometry\nx,y,z\nDX, MN, MNT"),
        ("风荷载层", "wind_forces.py\nKaimal spectrum\nDavenport coherence"),
        ("模型层", "TclWriter\nInput.tcl\n damping params"),
        ("求解层", "OpenSees\nstatic / modal\n time history"),
        ("判据层", "time_step\ncoverage audit\ncoverage_i"),
        ("汇总层", "aggregate\nresult package\ncurves / surfaces"),
    ]
    positions = [
        (0.06, 0.58), (0.30, 0.58), (0.54, 0.58), (0.78, 0.58),
        (0.18, 0.18), (0.42, 0.18), (0.66, 0.18),
    ]
    w, h = 0.17, 0.27
    colors = ["#EAF3F8", "#F6F8FB", "#EAF7F0", "#FFF7E8", "#FDECEC", "#EEF4FF", "#F7F7FA"]
    for i, (head, body) in enumerate(labels):
        x, y = positions[i]
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=colors[i], edgecolor="#B7C9DD", linewidth=1.1))
        ax.text(x + w / 2, y + h * 0.72, head, ha="center", va="center", fontsize=11, fontweight="bold", color="#1F4D78", fontproperties=font_prop)
        ax.text(x + w / 2, y + h * 0.35, body, ha="center", va="center", fontsize=8.0, color="#20242A", fontproperties=font_prop)
    for a, b in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]:
        xa, ya = positions[a]
        xb, yb = positions[b]
        start = (xa + w, ya + h / 2) if ya == yb else (xa + w / 2, ya)
        end = (xb, yb + h / 2) if ya == yb else (xb + w / 2, yb + h)
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", lw=1.2, color="#708090"))
    ax.text(0.5, 0.06, "每一层的输出都是下一层的输入；最终输出不是单一 yes/no，而是 coverage_i(L, u_star) 曲面。", ha="center", fontsize=10.5, color="#5D6773", fontproperties=font_prop)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def make_tcl_flow_figure() -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / "tcl_opensees_flow_cn.png"
    font_path = Path("C:/Windows/Fonts/msyh.ttc")
    font_prop = font_manager.FontProperties(fname=str(font_path)) if font_path.exists() else None
    fig, ax = plt.subplots(figsize=(10.8, 4.8), dpi=180)
    ax.axis("off")
    boxes = [
        ("Input.tcl", 0.05, 0.72, "#EAF3F8", "模型、节点、单元、荷载、recorders"),
        ("Static gravity", 0.36, 0.72, "#F6F8FB", "自重初始平衡"),
        ("Modal procedures", 0.67, 0.72, "#F6F8FB", "f1 与参与质量"),
        ("Path time series", 0.05, 0.38, "#EAF7F0", "风荷载文件 -> 节点力"),
        ("Wind_velocity_reader.tcl", 0.36, 0.38, "#EAF7F0", "节点风速 -> 单元风速"),
        ("Damping_shifter.tcl", 0.67, 0.38, "#FFF7E8", "xi_total -> setElementRayleigh"),
        ("dynamic2.tcl", 0.36, 0.08, "#FDECEC", "自适应瞬态步进 + 调用 adapt_damp"),
    ]
    for head, x, y, color, body in boxes:
        ax.add_patch(plt.Rectangle((x, y), 0.24, 0.17, facecolor=color, edgecolor="#B7C9DD", linewidth=1.1))
        ax.text(x + 0.12, y + 0.115, head, ha="center", va="center", fontsize=10.5, fontweight="bold", color="#1F4D78", fontproperties=font_prop)
        ax.text(x + 0.12, y + 0.055, body, ha="center", va="center", fontsize=8.2, color="#20242A", fontproperties=font_prop)
    arrows = [
        ((0.29, 0.805), (0.36, 0.805)),
        ((0.60, 0.805), (0.67, 0.805)),
        ((0.17, 0.72), (0.17, 0.55)),
        ((0.48, 0.72), (0.48, 0.55)),
        ((0.79, 0.72), (0.79, 0.55)),
        ((0.29, 0.465), (0.36, 0.465)),
        ((0.60, 0.465), (0.67, 0.465)),
        ((0.79, 0.38), (0.53, 0.25)),
        ((0.48, 0.38), (0.48, 0.25)),
    ]
    for a, b in arrows:
        ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="->", lw=1.15, color="#708090"))
    ax.text(0.5, 0.94, "OpenSees/Tcl 计算流程：模型定义、静力平衡、模态参数、动态荷载、气动阻尼更新、瞬态推进", ha="center", fontsize=12.5, fontweight="bold", color="#20242A", fontproperties=font_prop)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    workflow_fig = make_workflow_figure()
    tcl_fig = make_tcl_flow_figure()
    single = read_csv(SP / "single_point_summary.csv")

    doc = Document()
    style_doc(doc)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run("架空导线 Galloping 研究汇报材料")
    font(r, 22, True, BLUE)
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run("研究框架、代码工作流、limits 数学原理与两个范例 | 2026-06-10")
    font(r, 11, color=MUTED)
    callout(doc, "一句话主线", "本研究把“是否发生 galloping”的二值问题，转化为不同判据在时域中的覆盖率函数 coverage_i。当前汇报不展开 sweep 曲面结果，而是用两个范例说明：代码工作流是否可信，以及每个 limit 在数学上如何从 OpenSees 时程记录变成可统计的判定。")

    doc.add_heading("1. 本次汇报要回答什么", level=1)
    para(doc, "本次汇报分为四个层次。第一，解释模型与代码工作流如何从几何、材料和风速参数生成 OpenSees 模型，并把结果传递给判据审计。第二，解释 Tcl 文件在 OpenSees 中各自负责什么。第三，详细解释我们当前采用的 limits：负阻尼、delta 判别、位移增长响应、大位移和净空标准，重点说明它们的数学触发逻辑。第四，只展示两个范例：悬链线三测点单工况演示，以及三节点折线最小模型的 MATLAB/Python 工作流验证。")
    bullets(doc, [
        "研究变量：跨距 L、下垂高度 H、摩阻速度 u_star、随机 seed，以及未来要扩展的导线结构参数。",
        "核心输出：每个判据在每个工况中的 coverage_fraction，而不是仅仅输出发生/不发生。",
        "当前代表性模型：101 节点悬链线/近抛物线模型用于展示真实跨距响应；三节点折线最小模型用于检查 MATLAB/Python/OpenSees 工作流一致性。",
    ])

    doc.add_heading("2. 模型文件整理结果", level=1)
    para(doc, "本次已将固定 Tcl、Python 生成的 Tcl、MATLAB 验证副本生成的 Tcl，以及原始 TIMUR4 参考 Tcl 整理到一个展示包中。")
    simple_table(doc, ["内容", "路径"], [
        ["Tcl 展示包", str(OUT / "model_tcl_package")],
        ["Tcl 索引文件", str(OUT / "model_tcl_package" / "MODEL_TCL_INDEX.md")],
        ["清单 CSV", str(OUT / "model_tcl_package" / "model_tcl_manifest.csv")],
    ], 8.2)

    doc.add_heading("3. 代码工作流：每一步做什么、输入输出是什么", level=1)
    picture(doc, workflow_fig, "图 1  研究代码工作流：从配置、几何、风荷载、OpenSees 模型到逐时间步 limits 审计。", 6.85)
    simple_table(doc, ["步骤", "代码/命令", "输入", "输出并传递给哪里"], [
        ["1 配置读取", "config/*.yaml; config_loader.py", "L, Sag/H, material, analysis, time_history, solver", "统一 config 字典，传给 CableGeometry / TclWriter / wind_forces"],
        ["2 几何与质量", "src/cable_analyser/geometry.py", "geometry.type, L, Sag, discretisation, Dia, density/self_weight", "x,y,z, angle, element length dx, tributary DX, MN/MNT"],
        ["3 风场/荷载生成", "tools/generate_wind_forces.py; src/cable_analyser/wind_forces.py", "u_star, seed, geometry, coefficient tables", "NODE_i wind/force text files，供 Tcl Path timeSeries 使用"],
        ["4 Tcl 模型生成", "src/cable_analyser/tcl_writer.py", "config + geometry + modal frequency", "Input.tcl 与 inputs_aerodynamic_damping.tcl"],
        ["5 OpenSees 求解", "src/cable_analyser/solver.py; OpenSees.exe Input.tcl", "Input.tcl, force files, tcl_procedures", "Dynamic/Velocity/Accel/Reaction/Element/damping/solver logs"],
        ["6 单工况判据", "tools/time_step_coverage_audit.py --max-records 4096", "OpenSees time-stamped outputs", "C2/C4/C6/C7/C2&C4 coverage per case"],
        ["7 批量聚合", "tools/aggregate_l_ustar_coverage.py", "case_coverage.csv + failed cases", "后续 sweep 使用的大表、曲线、曲面、failed fraction"],
        ["8 报告/PPT", "build_*_report.py / deck scripts", "result_package + single_point_demo + validation outputs", "Word/PPT 汇报材料"],
    ], 7.2)

    doc.add_heading("4. Tcl/OpenSees 计算流程", level=1)
    picture(doc, tcl_fig, "图 2  Tcl 在 OpenSees 中的计算流程框架。", 6.85)
    para(doc, "Tcl 层的核心是：Input.tcl 不是单纯的几何文件，而是完整的 OpenSees 主输入文件；它定义模型、静力分析、模态分析、动力荷载、recorders、阻尼更新入口和瞬态循环入口。辅助 Tcl 文件则负责数据读取、插值、风速映射、动态阻尼和自适应步进。")
    simple_table(doc, ["Tcl 文件", "职责", "在计算流程中的位置"], [
        ["Input.tcl", "定义模型、材料、单元、边界、自重、气动荷载、recorders、求解器设置", "OpenSees 主入口"],
        ["inputs_aerodynamic_damping.tcl", "存储 MassM, B, L_e, ro_air, xi_structural, omegaN", "Damping_shifter.tcl 的参数输入"],
        ["Wind_velocity_reader.tcl", "读取节点风速并生成单元风速数组", "静力分析前 source，使动态阻尼可调用风速"],
        ["Damping_shifter.tcl", "计算相对风速、攻角、C_D、dC_L/dalpha、xi_total，并更新元素 Rayleigh 阻尼", "dynamic2 每步调用 adapt_damp"],
        ["dynamic2.tcl", "推进瞬态分析、处理自适应步长、调用已注册函数、记录实时状态", "动力分析循环"],
        ["PROCEDURE_Raf_6dof.tcl", "输出模态频率和参与质量", "静力平衡后 / 动力前"],
    ], 7.4)

    doc.add_heading("5. 几何线形、监测点与覆盖率指标", level=1)
    para(doc, "线形方案保留三类：type=1 抛物线，用于浅垂度近似；type=2 悬链线，用于当前生产研究与 Timur baseline；type=3 折线 V 形，用于最小三节点工作流测试。")
    simple_table(doc, ["线形", "用途", "当前状态"], [
        ["抛物线", "浅垂度解析近似和工程对照", "可作为备选几何"],
        ["悬链线", "真实跨距主模型，当前 L-u_star 曲面采用该类几何/近似匹配", "主生产模型"],
        ["折线三节点", "端点固定、中点自由的最小 OpenSees/Tcl 工作流验证", "MATLAB/Python 完全一致"],
    ])
    para(doc, "展示型单点监测选择三个点：1/4 span、midspan、3/4 span。选择原因是它们能覆盖对称跨的典型振型位置，并能观察跨中最大响应及两侧四分点的相位/阻尼差异。但生产判据不是单点判据，仍然在整根导线的全部节点或全部单元上计算。")
    para(doc, "覆盖率定义：如果一个 204.8 s 工况中，某个 limit 在 N_problem 个有效时间步上成立，总有效步数为 N_total，则 coverage_fraction = N_problem / N_total。当前审计使用 --max-records 4096，以避免 OpenSees 自适应子步造成统计权重偏置。")

    doc.add_heading("6. Limits：逐项定义、使用方式与来源", level=1)
    para(doc, "所有 limits 都先在离散时间步上定义。设 OpenSees 输出的有效记录为 t_k, k=1,...,N。对任意判据 i，我们先构造指示函数 I_i(t_k)，若该时间步满足判据则 I_i=1，否则 I_i=0。该工况下的覆盖率为 coverage_i = sum_k I_i(t_k) / N。若判据定义在节点 n 或单元 e 上，则先在该时间步做空间聚合：例如全线最大位移、负阻尼单元比例、最小有效阻尼，之后再转成时间步指示函数。")
    simple_table(doc, ["Limit", "定义", "如何使用", "来源/理由"], [
        ["delta 判别", "delta_D = C_D + dC_L/dalpha；alpha 以弧度计", "作为 Den Hartog 气动易感性检查；当前 dC_L 文件为每度导数，需乘 180/pi", "Week 7/Den Hartog；Rossi et al.; Chabart & Lilien"],
        ["负阻尼 C2", "xi_total = xi_structural + xi_aero；当 xi_total < 0 且达到元素比例/幅值阈值", "机理层 onset 信号；不单独代表大位移严重性", "Week 7 总阻尼变负；Rossi et al. 临界速度/总阻尼条件"],
        ["位移增长 C4", "20 s rolling p95 响应相对前一窗口或基准窗口增长", "过程层信号：区分随机振动和持续放大", "galloping 是低频大幅自激增长过程"],
        ["大位移 C6", "全线最大位移达到 0.10H", "状态层信号：当前最清晰的 developed-response 曲面", "大幅低频 galloping 定义；Chabart & Lilien limit-cycle/大响应"],
        ["净空 C7", "净空/相间距/张力等工程 limit-state 通道", "保留工程后果接口；当前未校准，不作为主结论", "EN 50341 / National Grid RICA / IEC 60826"],
        ["C2&C4", "同一时间步 C2 与 C4 同时成立", "严格同步标记，避免只看瞬时负阻尼", "机理与响应过程同时出现时更可信"],
    ], 7.0)
    doc.add_heading("6.1 delta 判别：气动功输入的符号检查", level=2)
    para(doc, "Den Hartog 型垂向驰振的核心量为 Delta_D(alpha) = C_D(alpha) + dC_L/dalpha。这里 alpha 必须以弧度计，因此若气动系数表给出的是每度导数，进入公式前必须乘以 180/pi。数学含义是：小扰动运动改变攻角后，升力斜率项和阻力项共同决定气动力在运动方向上的等效功输入趋势。若 Delta_D < 0，则气动力可能向结构输入能量，系统具有负气动阻尼倾向。")
    callout(doc, "逐时间步判定", "对每个单元 e 和时间步 t_k，由相对风速与结构速度得到瞬时攻角 alpha_e(t_k)，插值得到 C_D 与 dC_L/dalpha，并计算 Delta_D,e(t_k)。delta 覆盖率可以记为 I_delta(t_k)=1[某监测点或足够比例单元的 Delta_D,e(t_k)<0]。", "F8FBFF")

    doc.add_heading("6.2 C2 负阻尼：总阻尼是否越过零", level=2)
    para(doc, "C2 在 delta 判别之上进一步加入风速、质量、频率和结构阻尼。当前 Tcl 离散单元形式可写为 xi_total,e(t_k) = xi_structural + rho_air U_rel,e(t_k) B L_e Delta_D,e(t_k) / (4 M_e omega_n)。当 Delta_D 为负且风速足够大时，气动阻尼项为负；若它的绝对值超过结构阻尼，则 xi_total<0。")
    para(doc, "当前审计不把单个瞬时 xi_total<0 直接视为工况失败，而是要求负阻尼具有空间比例和幅值意义：例如负阻尼单元比例超过阈值，并且最小 xi_total 低于小的负值阈值。这样可以避免数值插值噪声或局部单元偶然触发。")

    doc.add_heading("6.3 C4 位移增长：响应是否在时间窗中持续放大", level=2)
    para(doc, "C4 不判断气动机理，而判断响应过程。设全线响应包络 r(t_k)=max_n sqrt(y_n(t_k)^2+z_n(t_k)^2)，把时间序列切成 20 s rolling windows，并计算每个窗口的 p95 响应 A_j。若 A_j/A_{j-1} 超过前窗增长阈值，或 A_j/A_0 超过基准增长阈值，则该窗口对应时间步记为 C4=1。当前工作流采用的典型阈值是相对前一窗口 1.20，以及相对基准窗口 1.50。")

    doc.add_heading("6.4 C6 大位移：是否已经进入可见的大响应状态", level=2)
    para(doc, "C6 是状态层判据。它不追问负阻尼来源，而是直接检查全线最大动态位移是否达到几何尺度阈值。当前定义为 r(t_k) >= 0.10H，其中 H 为该跨下垂高度。这个判据适合识别 developed galloping response：一旦触发，说明响应幅值已经具有明确工程可见性。")

    doc.add_heading("6.5 C7 净空标准与 C2&C4 组合判据", level=2)
    para(doc, "C7 是工程后果接口。数学上它应比较瞬时导线位置与净空、相间距、地线/相线间距或安全包络之间的剩余裕度，例如 clearance_margin(t_k)=clearance_required-clearance_available(t_k)。当 margin>0 时触发。当前 C7 仍是保留通道，尚未完成按 EN 50341、National Grid RICA 或具体塔型净空包络的校准，因此不作为本阶段主结论。")
    para(doc, "C2&C4 是组合判据，不是新的物理模型。它在同一时间步或同一窗口要求 I_C2(t_k)=1 且 I_C4(t_k)=1。它的意义是把“存在负阻尼机理”和“响应确实在增长”同步起来，因此比单独 C2 更保守，也比单独 C4 更有机理解释。")
    callout(doc, "汇报时需要强调", "C2、C4、C6、C7 不是互相替代的标签。C2 问“是否有自激机理”，C4 问“响应是否持续增长”，C6 问“是否已经形成工程上可见的大响应”，C7 问“是否触及工程后果”。")

    doc.add_heading("6.1 临界风速公式与当前演示模型数值", level=2)
    para(doc, "若采用 Den Hartog 型线性化思想，可以由总阻尼为零推导临界相对风速。需要注意公式中的质量定义：若使用单位长度质量 m，常见形式可写为 U_cr = 2 m xi omega_n / (rho B |dC_L/dalpha + C_D|)；而当前 Tcl 实现使用离散单元等效质量 M_e 和单元代表长度 L_e，代码一致形式为：")
    callout(doc, "代码一致临界相对风速", "U_cr,e = 4 M_e xi omega_n / (rho B L_e |Delta_D|), 其中 Delta_D = dC_L/dalpha + C_D。当前 dC_L 文件为每度导数，进入公式前必须转换为每弧度导数。", "F8FBFF")
    para(doc, "在单点演示的悬链线模型中，Tcl 阻尼参数为 MassM = 6.565677 kg, L_e = 4.049516 m, B = 0.02862 m, rho = 1.204 kg/m3, xi = 0.01, omega_n = 0.867627 rad/s。使用三测点的最不利 Delta_D，可得到局部临界相对风速约 0.0985 m/s。")
    simple_table(doc, ["监测点", "高度 z (m)", "U_cr by mean Delta (m/s)", "u_star eq. (m/s)", "U_cr by min Delta (m/s)", "u_star eq. (m/s)"], [
        ["1/4 span", "41.54", "0.1397", "0.00804", "0.0986", "0.00567"],
        ["Midspan", "38.92", "0.1375", "0.00799", "0.0985", "0.00573"],
        ["3/4 span", "41.54", "0.1381", "0.00795", "0.0985", "0.00567"],
    ], 7.0)
    para(doc, "这里的等效 u_star 使用 U(z)=u_star/kappa*log(z/z0) 反算，取 kappa=0.387, z0=0.05 m, 支座高度 49.4 m。演示工况 u_star=0.60 m/s 在导线高度对应的平均水平风速约 10.3-10.4 m/s，远高于上述 C2 线性临界值。")
    callout(doc, "解释口径", "这个很低的临界值不应直接解释为工程设计临界风速。它说明当前气动系数表在小攻角范围内给出很强的负 Delta_D，使 C2/负阻尼非常敏感。最终 L-u_star 临界边界仍应通过时域模拟的 C4/C6/C2&C4/failed-fraction 覆盖率曲面确定；U_cr 公式适合作为局部机理解释和 C2 的 sanity check。", "FFF4DE")

    doc.add_heading("7. 范例一：悬链线三测点单工况演示", level=1)
    picture(doc, SP / "monitor_points_geometry.png", "图 3  三个展示型监测点：1/4 span、midspan、3/4 span。", 5.8)
    rows = []
    for r in single:
        rows.append([
            r["monitor"], r["node"], f"{float(r['x_over_L']):.2f}",
            f"{float(r['max_abs_disp_x_m']):.2f}", f"{float(r['max_abs_disp_z_m']):.2f}",
            f"{float(r['negative_delta_D_fraction_from_wind_angle']):.3f}",
            f"{float(r['negative_xi_fraction_recorded']):.3f}",
        ])
    simple_table(doc, ["点位", "节点", "x/L", "max |x| m", "max |z| m", "delta<0", "xi<0"], rows, 7.8)
    picture(doc, SP / "displacement_x_timeseries.png", "图 4  三测点水平位移时程。", 6.7)
    picture(doc, SP / "displacement_z_timeseries.png", "图 5  三测点竖向位移时程。", 6.7)
    picture(doc, SP / "den_hartog_delta_timeseries.png", "图 6  三测点 Den Hartog delta_D 时程。", 6.7)
    picture(doc, SP / "damping_timeseries.png", "图 7  三测点相邻单元有效阻尼时程。", 6.7)

    doc.add_heading("8. 范例二：三节点折线最小模型工作流验证", level=1)
    para(doc, "三节点折线最小模型是最重要的工作流 sanity check：端点固定，中点自由，只有两个单元和一个可动节点。Python 与 MATLAB 都完整跑到 204.8 s，位移、速度、加速度、支座反力、阻尼日志共 33 个通道最大差异为 0。这说明在最简模型中，Python 迁移版与 MATLAB 原始工作流的核心 OpenSees/Tcl 流程完全一致。")
    simple_table(doc, ["验证", "结果", "解释"], [
        ["三节点折线", "33/33 通道完全一致，max diff = 0", "核心工作流一致"],
        ["悬链线三测点范例", "用于解释位移、delta_D、阻尼和轨迹时程", "展示 limits 如何作用于真实跨距模型"],
    ], 8.0)
    picture(doc, VAL / "broken_line_minimal_3node" / "comparison" / "middle_node_displacement_comparison.png", "图 8  三节点折线最小模型中点位移 MATLAB/Python 对比。", 6.5)

    doc.add_heading("10. 建议的会议讲法", level=1)
    numbered(doc, [
        "先说明研究目标已经从“找一个临界点”转为“得到多个判据的时域覆盖率函数”，但本次汇报不展开 sweep 曲面结果。",
        "再解释代码工作流，强调每一层输出如何传递到下一层，以及所有生产判据都基于 time-stamped OpenSees 输出。",
        "然后单独讲 limits：C2 是机理，C4 是增长过程，C6 是已发展大响应，C7 是工程后果接口。",
        "展示悬链线三测点范例，说明位移、delta_D、阻尼和各 limit 如何在同一时程中被解释。",
        "展示三节点折线验证，证明基础 MATLAB/Python/OpenSees 工作流一致；最后说明 sweep 曲面是下一阶段用于趋势研究的输出，而不是本次汇报重点。",
    ])

    doc.add_page_break()
    doc.add_heading("附录 A：关键路径", level=1)
    simple_table(doc, ["项目", "路径"], [
        ["Tcl 展示包", str(OUT / "model_tcl_package")],
        ["单点结果", str(SP)],
        ["后续 sweep 结果包（本次不重点展示）", str(PKG)],
        ["三节点验证报告", str(VAL / "broken_line_minimal_3node" / "comparison" / "broken_line_minimal_validation_report.md")],
        ["悬链线验证报告", str(VAL / "matlab_python_force3_baseline" / "comparison" / "workflow_validation_report.md")],
        ["判据设计文件", str(ROOT / "GALLOPING_CRITERIA.md")],
    ], 7.2)

    doc.save(DOCX_PATH)
    print(DOCX_PATH)


if __name__ == "__main__":
    main()
