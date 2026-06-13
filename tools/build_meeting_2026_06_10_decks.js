const fs = require("fs");
const path = require("path");
const PptxGenJS = require("pptxgenjs");

const ROOT = "D:/Pyprogramme/pylon1";
const OUT = path.join(ROOT, "output", "reports", "meeting_2026_06_10");
const PKG = path.join(ROOT, "output", "time_step_coverage_audit", "L300_350_400_ustar_grid_n4096_s3_plus_extra", "result_package");
const SP = path.join(ROOT, "output", "single_point_demo", "L322P8_U0P600_SEED20260909");
const VAL = path.join(ROOT, "output", "workflow_validation");
const FIG = path.join(OUT, "figures");

fs.mkdirSync(OUT, { recursive: true });

const C = {
  navy: "1F4D78",
  blue: "2E74B5",
  teal: "0E7C86",
  green: "4A8F5A",
  amber: "C7832B",
  red: "B24A4A",
  ink: "20242A",
  gray: "5D6773",
  pale: "F4F7FB",
  line: "B7C9DD",
  white: "FFFFFF",
};

function deck(lang) {
  const zh = lang === "zh";
  const pptx = new PptxGenJS();
  pptx.defineLayout({ name: "WIDE", width: 13.333, height: 7.5 });
  pptx.layout = "WIDE";
  pptx.author = "pylon1 galloping research";
  pptx.subject = zh ? "Galloping 研究框架与汇报" : "Galloping research framework and results";
  pptx.title = zh ? "架空导线 Galloping 研究汇报" : "Overhead Conductor Galloping Study";
  pptx.company = "pylon1";
  pptx.lang = zh ? "zh-CN" : "en-GB";
  pptx.theme = {
    headFontFace: zh ? "Microsoft YaHei" : "Aptos Display",
    bodyFontFace: zh ? "Microsoft YaHei" : "Aptos",
    lang: zh ? "zh-CN" : "en-GB",
  };

  const font = zh ? "Microsoft YaHei" : "Aptos";
  const titleFont = zh ? "Microsoft YaHei" : "Aptos Display";
  let n = 1;

  function footer(slide) {
    slide.addShape(pptx.ShapeType.line, { x: 0.55, y: 7.02, w: 12.2, h: 0, line: { color: "D7E0EA", width: 0.8 } });
    slide.addText(zh ? "pylon1 galloping research | 2026-06-10" : "pylon1 galloping research | 10 Jun 2026", {
      x: 0.62, y: 7.12, w: 8.6, h: 0.18, fontFace: font, fontSize: 7.2, color: "7B8794",
    });
    slide.addText(String(n).padStart(2, "0"), { x: 12.35, y: 7.08, w: 0.4, h: 0.18, fontFace: font, fontSize: 8, color: "7B8794", align: "right" });
    n += 1;
  }

  function title(slide, text, kicker) {
    if (kicker) slide.addText(kicker, { x: 0.62, y: 0.25, w: 11.8, h: 0.22, fontFace: font, fontSize: 8.4, bold: true, color: C.teal, charSpace: 0.4 });
    slide.addText(text, { x: 0.62, y: 0.55, w: 12.0, h: 0.54, fontFace: titleFont, fontSize: 22, bold: true, color: C.ink, fit: "shrink" });
    slide.addShape(pptx.ShapeType.line, { x: 0.62, y: 1.18, w: 12.0, h: 0, line: { color: "D6DEE8", width: 1 } });
  }

  function claim(slide, text, y = 1.34) {
    slide.addShape(pptx.ShapeType.roundRect, { x: 0.72, y, w: 11.9, h: 0.56, rectRadius: 0.04, fill: { color: "EAF3F8" }, line: { color: "CFE2EE", width: 0.8 } });
    slide.addText(text, { x: 0.95, y: y + 0.12, w: 11.45, h: 0.28, fontFace: font, fontSize: 12.5, bold: true, color: C.navy, fit: "shrink" });
  }

  function box(slide, x, y, w, h, head, body, accent = C.blue, fill = C.white) {
    slide.addShape(pptx.ShapeType.rect, { x, y, w, h, fill: { color: fill }, line: { color: C.line, width: 0.75 } });
    slide.addShape(pptx.ShapeType.rect, { x, y, w: 0.08, h, fill: { color: accent }, line: { color: accent } });
    slide.addText(head, { x: x + 0.22, y: y + 0.12, w: w - 0.35, h: 0.25, fontFace: font, fontSize: 10.6, bold: true, color: accent, fit: "shrink" });
    slide.addText(body, { x: x + 0.22, y: y + 0.46, w: w - 0.36, h: h - 0.52, fontFace: font, fontSize: 9.3, color: C.ink, fit: "shrink", valign: "top", breakLine: false });
  }

  function bullets(slide, items, x, y, w, h, size = 11.2) {
    slide.addText(items.map(t => ({ text: t, options: { bullet: { type: "bullet" }, breakLine: true } })), {
      x, y, w, h, fontFace: font, fontSize: size, color: C.ink, paraSpaceAfterPt: 6, fit: "shrink", valign: "top",
    });
  }

  function table(slide, rows, x, y, w, h, colW, size = 8.0) {
    slide.addTable(rows, {
      x, y, w, h, colW, margin: 0.055,
      border: { type: "solid", color: C.line, pt: 0.55 },
      fontFace: font, fontSize: size, color: C.ink, valign: "mid", fit: "shrink",
      autoFit: false,
    });
  }

  function img(slide, file, x, y, w, h) {
    if (fs.existsSync(file)) slide.addImage({ path: file, x, y, w, h });
    else box(slide, x, y, w, h, "Missing image", file, C.red, "FFF0F0");
  }

  let s;

  s = pptx.addSlide();
  s.background = { color: "F7FAFD" };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.18, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText(zh ? "架空导线 Galloping 研究" : "Overhead Conductor Galloping Study", { x: 0.72, y: 0.88, w: 10.8, h: 0.35, fontFace: font, fontSize: 13, bold: true, color: C.teal });
  s.addText(zh ? "研究框架、代码工作流、Limits 数学原理与两个范例" : "Framework, Code Workflow, Limit Mathematics and Two Examples", { x: 0.72, y: 1.42, w: 11.2, h: 0.7, fontFace: titleFont, fontSize: zh ? 27 : 26, bold: true, color: C.ink, fit: "shrink" });
  s.addText(zh ? "目标：说明 limits 如何由 OpenSees 时程记录转化为覆盖率判定" : "Target: explain how OpenSees histories become limit-coverage decisions", { x: 0.74, y: 2.28, w: 11.3, h: 0.3, fontFace: font, fontSize: 13, color: C.gray, fit: "shrink" });
  box(s, 0.85, 3.15, 3.55, 1.1, zh ? "研究问题" : "Question", zh ? "跨距 L 与摩阻速度 u_star 如何共同影响 galloping 风险？" : "How do span L and friction velocity u_star jointly affect galloping risk?", C.blue);
  box(s, 4.85, 3.15, 3.55, 1.1, zh ? "方法" : "Method", zh ? "OpenSees 时程模拟 + 多 limits 覆盖率审计" : "OpenSees time-history simulation plus multi-limit coverage audit", C.teal);
  box(s, 8.85, 3.15, 3.55, 1.1, zh ? "输出" : "Output", zh ? "C2/C4/C6/C7 覆盖率与两个范例解释" : "C2/C4/C6/C7 coverage and two worked examples", C.green);
  s.addText(zh ? "Meeting materials | 2026-06-10" : "Meeting materials | 10 Jun 2026", { x: 0.78, y: 6.75, w: 5.5, h: 0.22, fontFace: font, fontSize: 9, color: "8A96A3" });
  footer(s);

  s = pptx.addSlide(); title(s, zh ? "汇报主线" : "Main Story", "SUMMARY");
  claim(s, zh ? "我们将 galloping 从“是否发生”转为“不同判据在 L-u_star 空间内的覆盖率函数”。" : "We move from a yes/no galloping flag to coverage functions over L-u_star space.");
  box(s, 0.72, 2.15, 3.7, 2.0, zh ? "为什么" : "Why", zh ? "随机风场下 galloping 可能只在部分时间窗口出现；单一临界点会丢失趋势。" : "In stochastic wind, galloping indicators may appear only in time windows; one critical point hides trends.", C.blue);
  box(s, 4.82, 2.15, 3.7, 2.0, zh ? "本次展示范围" : "Scope Today", zh ? "不展开 sweep 曲面结果；只用两个范例解释工作流与判据。" : "No sweep maps today; two examples explain the workflow and criteria.", C.green);
  box(s, 8.92, 2.15, 3.7, 2.0, zh ? "需要谨慎解释" : "Use With Care", zh ? "C2 是机理指标；C4 有随机 realization 敏感性；C7 尚未按真实净空校准。" : "C2 is mechanistic; C4 is realization-sensitive; C7 still needs real clearance calibration.", C.amber);
  bullets(s, zh ? [
    "变量框架仍保留 L、H、u_star 和 seed；本次只展示代表性单工况。",
    "输出重点是每个 limit 的逐时间步数学判定，而不是 sweep 结果。",
    "验证：三节点折线模型 MATLAB/Python 全记录完全一致。"
  ] : [
    "The variable framework still includes L, H, u_star and seed; today we show representative cases only.",
    "The focus is the per-time-step mathematics of each limit, not sweep results.",
    "Validation: MATLAB and Python match exactly in the three-node broken-line model."
  ], 0.92, 4.95, 11.6, 1.2);
  footer(s);

  s = pptx.addSlide(); title(s, zh ? "代码工作流" : "Code Workflow", "WORKFLOW");
  claim(s, zh ? "每一层输出都是下一层输入；最终输出是 coverage_i(L,u_star)，不是单次最大值。" : "Each layer feeds the next; the final output is coverage_i(L,u_star), not a single maximum.");
  img(s, path.join(FIG, "code_workflow_cn.png"), 0.75, 1.95, 11.9, 4.1);
  bullets(s, zh ? [
    "配置 YAML 控制几何、材料、u_star、seed 和求解器。",
    "TclWriter 写出 Input.tcl 与 aerodynamic damping 参数。",
    "time_step_coverage_audit 将响应时程转为逐时间步 limits coverage。"
  ] : [
    "YAML controls geometry, material, u_star, seed and solver settings.",
    "TclWriter emits Input.tcl and aerodynamic damping parameters.",
    "time_step_coverage_audit converts histories into per-time-step limit coverage."
  ], 0.9, 6.22, 11.2, 0.65, 9.5);
  footer(s);

  s = pptx.addSlide(); title(s, zh ? "Tcl / OpenSees 计算流程" : "Tcl / OpenSees Computation Flow", "MODEL FILES");
  claim(s, zh ? "Input.tcl 是主模型文件；其他 Tcl 负责读取、插值、风速映射、气动阻尼和自适应瞬态推进。" : "Input.tcl is the main model file; other Tcl files handle reading, interpolation, wind mapping, damping updates and transient stepping.");
  img(s, path.join(FIG, "tcl_opensees_flow_cn.png"), 0.8, 1.85, 11.7, 4.65);
  footer(s);

  s = pptx.addSlide(); title(s, zh ? "模型与监测点" : "Geometry and Monitor Points", "MODEL SETUP");
  claim(s, zh ? "生产判据是全线/全单元 coverage；单点监测只用于展示和解释。" : "Production criteria use full-line/all-element coverage; point monitors are for explanation.");
  img(s, path.join(SP, "monitor_points_geometry.png"), 0.75, 1.78, 5.8, 3.45);
  box(s, 7.0, 1.85, 5.3, 1.1, zh ? "三种线形" : "Geometry Options", zh ? "抛物线：浅垂度近似\n悬链线：生产研究主模型\n折线：三节点工作流验证" : "Parabola: shallow-sag approximation\nCatenary: production research model\nBroken line: three-node workflow validation", C.blue);
  box(s, 7.0, 3.25, 5.3, 1.1, zh ? "三测点" : "Three Monitors", zh ? "1/4 span, midspan, 3/4 span；用于解释时程、阻尼和气动系数。" : "1/4 span, midspan, 3/4 span; used to explain histories, damping and aerodynamic coefficients.", C.green);
  box(s, 7.0, 4.65, 5.3, 1.1, zh ? "覆盖率指标" : "Coverage Metric", zh ? "coverage = problem_time_steps / total_valid_time_steps；当前固定 4096 目标记录。" : "coverage = problem_time_steps / total_valid_time_steps; current audit fixes 4096 target records.", C.amber);
  footer(s);

  s = pptx.addSlide(); title(s, zh ? "Limits 设计原则" : "Limit Design Principle", "LIMITS");
  claim(s, zh ? "机理、响应和工程后果分开记录；本阶段不把所有判据直接取交集。" : "Mechanism, response and engineering consequence are stored separately; no premature intersection rule.");
  box(s, 0.75, 2.1, 3.65, 2.2, zh ? "机理层" : "Mechanism", zh ? "delta_D < 0\nxi_total < 0\n回答：是否具备自激条件？" : "delta_D < 0\nxi_total < 0\nQuestion: is self-excitation possible?", C.blue);
  box(s, 4.85, 2.1, 3.65, 2.2, zh ? "响应层" : "Response", zh ? "rolling p95 growth\nlarge displacement\n回答：是否发展成可见响应？" : "rolling p95 growth\nlarge displacement\nQuestion: has visible response developed?", C.green);
  box(s, 8.95, 2.1, 3.65, 2.2, zh ? "后果层" : "Consequence", zh ? "clearance / spacing / tension\n回答：是否触及工程限制？" : "clearance / spacing / tension\nQuestion: are engineering limits reached?", C.amber);
  bullets(s, zh ? [
    "C2 是 onset 机制信号，不等于严重程度。",
    "C4/C6 用来确认响应发展。",
    "C7 保留工程标准接口，但目前不作为主结论。"
  ] : [
    "C2 is an onset-mechanism signal, not severity by itself.",
    "C4/C6 confirm response development.",
    "C7 preserves the standards interface but is not the current primary conclusion."
  ], 1.0, 5.05, 11.3, 1.0);
  footer(s);

  s = pptx.addSlide(); title(s, zh ? "Limits 的定义与来源" : "Limit Definitions and Basis", "LIMITS");
  table(s, [
    [zh ? "Limit" : "Limit", zh ? "定义" : "Definition", zh ? "作用" : "Use", zh ? "来源" : "Basis"],
    ["delta_D", "C_D + dC_L/dalpha", zh ? "Den Hartog 气动易感性" : "Den Hartog susceptibility", "Week 7 / Den Hartog / Rossi"],
    ["C2", "xi_total < 0", zh ? "负总阻尼 onset 机制" : "negative-total-damping onset", "Week 7 / Rossi / ICWE"],
    ["C4", "20 s rolling p95 growth", zh ? "持续增长过程" : "sustained growth process", "galloping response development"],
    ["C6", "disp >= 0.10H", zh ? "已发展大响应" : "developed large response", "large-amplitude galloping"],
    ["C7", "clearance / spacing proxy", zh ? "工程后果接口" : "engineering consequence channel", "EN 50341 / RICA / IEC"],
  ], 0.65, 1.85, 12.0, 4.4, [1.0, 2.8, 3.7, 4.5], 7.6);
  footer(s);

  s = pptx.addSlide(); title(s, zh ? "Limits 的数学框架" : "Mathematical Structure of Limits", "LIMITS");
  claim(s, zh ? "每个 limit 先变成逐时间步指示函数，再统计覆盖率。" : "Each limit first becomes a per-time-step indicator, then a coverage fraction.");
  box(s, 0.75, 2.0, 3.75, 1.55, zh ? "时间离散" : "Time Discretisation",
    zh ? "OpenSees 输出有效记录 t_k, k=1,...,N。\n当前审计固定 4096 个目标记录。" : "OpenSees gives valid records t_k, k=1,...,N.\nThe current audit uses 4096 target records.",
    C.blue);
  box(s, 4.8, 2.0, 3.75, 1.55, zh ? "指示函数" : "Indicator",
    zh ? "I_i(t_k)=1：第 k 步满足 limit i。\nI_i(t_k)=0：第 k 步未满足。" : "I_i(t_k)=1 when limit i is met.\nI_i(t_k)=0 otherwise.",
    C.teal);
  box(s, 8.85, 2.0, 3.75, 1.55, zh ? "覆盖率" : "Coverage",
    zh ? "coverage_i = sum I_i(t_k) / N。\n它表示问题窗口占总有效时长的比例。" : "coverage_i = sum I_i(t_k) / N.\nIt is the fraction of problematic valid time.",
    C.green);
  bullets(s, zh ? [
    "若判据定义在节点上，先取全线最大响应或监测节点响应。",
    "若判据定义在单元上，先计算负阻尼单元比例、最小阻尼等空间聚合量。",
    "因此输出不是单次最大值，而是随时间持续程度。"
  ] : [
    "For node-based criteria, use the line maximum or selected monitor response.",
    "For element-based criteria, aggregate negative-damping fraction, minimum damping, etc.",
    "The output is persistence over time, not a single maximum."
  ], 0.95, 4.25, 11.5, 1.35, 11.0);
  footer(s);

  s = pptx.addSlide(); title(s, zh ? "delta 判别与 C2 负阻尼" : "Delta Criterion and C2 Negative Damping", "LIMITS");
  claim(s, zh ? "delta_D 判断气动能量输入趋势；C2 判断结构阻尼是否被气动负阻尼抵消。" : "delta_D checks aerodynamic energy-input tendency; C2 checks whether aerodynamic damping overwhelms structural damping.");
  box(s, 0.72, 1.95, 5.85, 1.55, zh ? "Den Hartog delta" : "Den Hartog Delta",
    zh ? "Delta_D(alpha)=C_D(alpha)+dC_L/dalpha\n若 Delta_D<0，气动力可能向运动输入能量。" : "Delta_D(alpha)=C_D(alpha)+dC_L/dalpha\nIf Delta_D<0, aerodynamic force may feed energy into motion.",
    C.blue);
  box(s, 6.86, 1.95, 5.75, 1.55, zh ? "C2 总阻尼" : "C2 Total Damping",
    zh ? "xi_total = xi_structural + rho U_rel B L_e Delta_D /(4 M_e omega_n)\n若 xi_total<0，则触发负阻尼窗口。" : "xi_total = xi_structural + rho U_rel B L_e Delta_D /(4 M_e omega_n)\nIf xi_total<0, a negative-damping window is triggered.",
    C.green);
  bullets(s, zh ? [
    "alpha 以弧度计；若 dC_L 文件是每度导数，必须乘 180/pi。",
    "C2 不是严重程度指标；它是 onset 机理指标。",
    "审计中还会检查负阻尼的空间比例和最小 xi_total，避免局部数值噪声。"
  ] : [
    "alpha is in radians; per-degree dC_L data must be multiplied by 180/pi.",
    "C2 is not a severity metric; it is an onset-mechanism metric.",
    "The audit also checks spatial fraction and minimum xi_total to avoid local numerical noise."
  ], 0.95, 4.15, 11.45, 1.35, 11.0);
  footer(s);

  s = pptx.addSlide(); title(s, zh ? "C4 增长与 C6 大响应" : "C4 Growth and C6 Large Response", "LIMITS");
  claim(s, zh ? "C4 问“是否持续放大”；C6 问“是否已经大到工程上可见”。" : "C4 asks whether the response is growing; C6 asks whether it is already visibly large.");
  box(s, 0.72, 1.95, 5.85, 1.75, zh ? "C4 rolling p95 增长" : "C4 Rolling p95 Growth",
    zh ? "r(t)=max_n sqrt(y_n^2+z_n^2)\n20 s 窗口 p95 为 A_j。\nA_j/A_{j-1}>=1.20 或 A_j/A_0>=1.50 时触发。" : "r(t)=max_n sqrt(y_n^2+z_n^2)\nA_j is the 20 s window p95.\nTriggered when A_j/A_{j-1}>=1.20 or A_j/A_0>=1.50.",
    C.teal);
  box(s, 6.86, 1.95, 5.75, 1.75, zh ? "C6 大位移状态" : "C6 Large Displacement",
    zh ? "若 r(t_k) >= 0.10H，则 I_C6(t_k)=1。\nH 是该跨下垂高度。" : "If r(t_k) >= 0.10H, then I_C6(t_k)=1.\nH is the sag of that span.",
    C.green);
  bullets(s, zh ? [
    "C4 是过程层信号，可区分随机振动和持续放大。",
    "C6 是状态层信号，适合描述 developed galloping response。",
    "两者与 C2 分开记录，避免把机理、过程和后果混成一个标签。"
  ] : [
    "C4 is a process signal separating random vibration from sustained growth.",
    "C6 is a state signal for developed galloping response.",
    "Both are stored separately from C2 to avoid mixing mechanism, process and consequence."
  ], 0.95, 4.25, 11.45, 1.25, 11.0);
  footer(s);

  s = pptx.addSlide(); title(s, zh ? "C7 净空与组合判据" : "C7 Clearance and Combined Criteria", "LIMITS");
  claim(s, zh ? "C7 是工程后果接口；C2&C4 是同步条件，不是新的物理模型。" : "C7 is the engineering-consequence interface; C2&C4 is a coincidence rule, not a new physical model.");
  box(s, 0.72, 1.95, 5.85, 1.75, zh ? "C7 净空/相间距" : "C7 Clearance / Spacing",
    zh ? "clearance_margin(t)=required - available(t)。\n当 margin>0，说明触及净空或相间距 limit-state。\n当前仍待按真实标准和塔型校准。" : "clearance_margin(t)=required - available(t).\nWhen margin>0, the clearance or phase-spacing limit-state is exceeded.\nIt still requires calibration to real standards and tower geometry.",
    C.amber);
  box(s, 6.86, 1.95, 5.75, 1.75, zh ? "C2&C4 同步" : "C2&C4 Coincidence",
    zh ? "I_C2C4(t)=I_C2(t) AND I_C4(t)。\n含义：负阻尼机理与响应增长同时出现。" : "I_C2C4(t)=I_C2(t) AND I_C4(t).\nMeaning: negative-damping mechanism and response growth occur together.",
    C.blue);
  bullets(s, zh ? [
    "C7 的文献/标准入口包括 EN 50341、National Grid RICA 和 IEC 60826。",
    "C2&C4 比单独 C2 更保守，也比单独 C4 更有机理解释。",
    "failed/non-normal run 是数值状态记录，不是正式 galloping limit。"
  ] : [
    "C7 is linked to EN 50341, National Grid RICA and IEC 60826.",
    "C2&C4 is more conservative than C2 alone and more mechanistic than C4 alone.",
    "A failed/non-normal run is a numerical status record, not a formal galloping limit."
  ], 0.95, 4.25, 11.45, 1.25, 11.0);
  footer(s);

  s = pptx.addSlide(); title(s, zh ? "临界风速公式：它解释 C2，但不是最终边界" : "Critical Wind Speed Formula: Explains C2, Not the Final Boundary", "U_CR");
  claim(s, zh ? "当前演示模型的局部负阻尼临界相对风速约 0.0985 m/s，折算 u_star 约 0.0057 m/s。" : "The local negative-damping critical relative speed in the demo case is about 0.0985 m/s, equivalent to u_star about 0.0057 m/s.");
  box(s, 0.72, 2.02, 5.65, 1.55, zh ? "代码一致公式" : "Code-consistent formula",
    zh ? "U_cr,e = 4 M_e xi omega_n / (rho B L_e |Delta_D|)\nDelta_D = dC_L/dalpha + C_D" : "U_cr,e = 4 M_e xi omega_n / (rho B L_e |Delta_D|)\nDelta_D = dC_L/dalpha + C_D",
    C.blue, "FFFFFF");
  box(s, 6.75, 2.02, 5.65, 1.55, zh ? "为什么不是直接工程临界" : "Why this is not the design critical speed",
    zh ? "它是局部线性负阻尼阈值。\n最终边界仍需看 C4/C6/C2&C4/failed-fraction 的时域覆盖率。" : "It is a local linear negative-damping threshold.\nThe final boundary still comes from C4/C6/C2&C4/failed-fraction time-domain coverage.",
    C.amber, "FFFFFF");
  table(s, [
    [zh ? "点位" : "Monitor", "z (m)", "U_cr mean Delta", "u_star eq.", "U_cr min Delta", "u_star eq."],
    ["1/4 span", "41.54", "0.1397", "0.00804", "0.0986", "0.00567"],
    ["Midspan", "38.92", "0.1375", "0.00799", "0.0985", "0.00573"],
    ["3/4 span", "41.54", "0.1381", "0.00795", "0.0985", "0.00567"],
  ], 0.78, 4.05, 11.8, 1.45, [1.7, 1.15, 2.2, 1.75, 2.2, 1.75], 7.3);
  bullets(s, zh ? [
    "演示工况 u_star = 0.60 m/s 在导线高度对应平均风速约 10.3-10.4 m/s。",
    "很低的 U_cr 说明当前气动表让 C2 很敏感；C2 应解释为机理层 onset，而非严重程度。"
  ] : [
    "The demo case u_star = 0.60 m/s corresponds to a mean conductor-height wind speed of about 10.3-10.4 m/s.",
    "The very low U_cr means the current aerodynamic table makes C2 highly sensitive; C2 is a mechanism-level onset indicator, not severity."
  ], 0.95, 5.9, 11.5, 0.7, 9.2);
  footer(s);

  s = pptx.addSlide(); title(s, zh ? "单点展示：位移响应" : "Point Demo: Displacement Response", "POINT RESULTS");
  img(s, path.join(SP, "displacement_x_timeseries.png"), 0.55, 1.55, 6.1, 4.65);
  img(s, path.join(SP, "displacement_z_timeseries.png"), 6.78, 1.55, 6.0, 4.65);
  claim(s, zh ? "单点图解释响应形态；正式 limits 仍按全线节点/单元计算。" : "Point plots explain response shape; formal limits still use all nodes/elements.", 6.35);
  footer(s);

  s = pptx.addSlide(); title(s, zh ? "单点展示：delta_D 与阻尼" : "Point Demo: delta_D and Damping", "MECHANISM");
  img(s, path.join(SP, "den_hartog_delta_timeseries.png"), 0.55, 1.55, 6.1, 4.65);
  img(s, path.join(SP, "damping_timeseries.png"), 6.78, 1.55, 6.0, 4.65);
  claim(s, zh ? "delta_D 解释气动易感性；xi_total 解释结构-气动组合后的负阻尼窗口。" : "delta_D explains aerodynamic susceptibility; xi_total includes structural and aerodynamic damping.", 6.35);
  footer(s);

  s = pptx.addSlide(); title(s, zh ? "三测点统计摘要" : "Three-Monitor Summary", "POINT SUMMARY");
  table(s, [
    [zh ? "点位" : "Monitor", "Node", "x/L", "max |x| m", "max |z| m", "delta<0", "xi<0"],
    ["1/4 span", "26", "0.25", "1.87", "5.28", "0.993", "0.351"],
    ["Midspan", "51", "0.50", "2.81", "6.87", "0.997", "0.324"],
    ["3/4 span", "76", "0.75", "2.17", "5.21", "0.996", "0.660"],
  ], 1.0, 1.95, 11.4, 2.0, [2.0, 1.0, 1.0, 1.5, 1.5, 1.7, 1.7], 8.2);
  box(s, 1.0, 4.45, 11.4, 1.25, zh ? "解释" : "Interpretation", zh ? "3/4 span 的负阻尼比例较高，但不是“始终为负”。这些单点统计用于机制解释，不替代全线 coverage。" : "The 3/4 span has a higher negative-damping fraction, but it is not always negative. These point statistics explain the mechanism and do not replace line-level coverage.", C.amber);
  footer(s);

  s = pptx.addSlide(); title(s, zh ? "工作流验证：三节点折线模型" : "Workflow Validation: Three-Node Broken Line", "VALIDATION");
  img(s, path.join(VAL, "broken_line_minimal_3node", "comparison", "middle_node_displacement_comparison.png"), 0.75, 1.45, 7.0, 5.2);
  box(s, 8.05, 1.75, 4.4, 1.15, zh ? "模型" : "Model", zh ? "3 节点，2 单元，端点固定，中点自由。" : "3 nodes, 2 elements, fixed ends, free middle node.", C.blue);
  box(s, 8.05, 3.15, 4.4, 1.15, zh ? "结果" : "Result", zh ? "位移、速度、加速度、反力、阻尼日志：33/33 通道完全一致。" : "Displacement, velocity, acceleration, reaction and damping logs: 33/33 channels match exactly.", C.green);
  box(s, 8.05, 4.55, 4.4, 1.15, zh ? "意义" : "Meaning", zh ? "基础 Tcl/OpenSees 工作流迁移可信。" : "The core Tcl/OpenSees workflow migration is credible.", C.amber);
  footer(s);

  s = pptx.addSlide(); title(s, zh ? "当前结论与下一步" : "Conclusions and Next Steps", "NEXT");
  bullets(s, zh ? [
    "工作流层面：三节点折线模型 MATLAB/Python/OpenSees 全记录完全一致。",
    "判据层面：C2、C4、C6、C7 分别对应机理、增长、状态和工程后果，不应过早合并。",
    "展示层面：本次只展示悬链线三测点范例与三节点折线验证，不展示 sweep 曲面结果。",
    "下一步：校准 C7 的真实净空/相间距标准；再用同一套 limits 进入 L-u_star sweep 趋势研究。"
  ] : [
    "Workflow: the three-node broken-line model matches exactly across MATLAB/Python/OpenSees records.",
    "Criteria: C2, C4, C6 and C7 represent mechanism, growth, state and engineering consequence, so they should not be merged too early.",
    "Presentation: today shows only the catenary three-monitor example and the three-node broken-line validation, not sweep maps.",
    "Next: calibrate C7 with real clearance/phase-spacing limits, then use the same limits for L-u_star sweep trend studies."
  ], 1.05, 1.65, 11.2, 3.2, 13);
  box(s, 1.05, 5.35, 11.2, 0.8, zh ? "推荐会议表述" : "Recommended framing", zh ? "我们先把机制和判据讲清楚，再把同一套判据推广到批量 sweep。" : "We first make the mechanism and criteria clear, then extend the same criteria to batch sweeps.", C.green, "F2FAF4");
  footer(s);

  const outName = zh ? "Galloping_Meeting_CN_2026_06_10.pptx" : "Galloping_Meeting_EN_2026_06_10.pptx";
  return pptx.writeFile({ fileName: path.join(OUT, outName) });
}

deck("zh").then(() => deck("en")).then(() => {
  fs.writeFileSync(path.join(OUT, "deck_manifest.json"), JSON.stringify({
    cn: path.join(OUT, "Galloping_Meeting_CN_2026_06_10.pptx"),
    en: path.join(OUT, "Galloping_Meeting_EN_2026_06_10.pptx"),
    slides_each: 17,
  }, null, 2), "utf8");
});
