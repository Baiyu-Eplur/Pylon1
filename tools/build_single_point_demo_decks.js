const fs = require("fs");
const path = require("path");
const PptxGenJS = require("C:/Users/haoya/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/pptxgenjs/dist/pptxgen.cjs.js");

const ROOT = "D:/Pyprogramme/pylon1";
const PKG = path.join(ROOT, "output", "single_point_demo", "L322P8_U0P600_SEED20260909");
const OUT = path.join(ROOT, "output", "reports", "single_point_demo_decks");
fs.mkdirSync(OUT, { recursive: true });

const C = {
  ink: "1E252D",
  gray: "5E6A75",
  pale: "F4F7FA",
  blue: "2E74B5",
  teal: "0E7C86",
  green: "4A8F5A",
  amber: "C7832B",
  red: "B24A4A",
  line: "C9D6E2",
  white: "FFFFFF",
};

function readCsv(file) {
  const text = fs.readFileSync(file, "utf8").trim();
  const [head, ...lines] = text.split(/\r?\n/);
  const cols = head.replace(/^\uFEFF/, "").split(",");
  return lines.map((line) => {
    const parts = line.split(",");
    const row = {};
    cols.forEach((col, i) => row[col] = parts[i]);
    return row;
  });
}

const summary = readCsv(path.join(PKG, "single_point_summary.csv"));
const meta = JSON.parse(fs.readFileSync(path.join(PKG, "single_point_demo_metadata.json"), "utf8"));

function fmt(value, digits = 3) {
  const n = Number(value);
  if (!Number.isFinite(n)) return String(value);
  return n.toFixed(digits);
}

function deck(lang) {
  const zh = lang === "zh";
  const pptx = new PptxGenJS();
  pptx.defineLayout({ name: "WIDE", width: 13.333, height: 7.5 });
  pptx.layout = "WIDE";
  pptx.author = "pylon1 galloping research";
  pptx.subject = zh ? "三测点 galloping 范例结果" : "Three-point galloping demonstration";
  pptx.title = zh ? "架空导线 Galloping 研究框架与单点监测范例" : "Overhead Conductor Galloping Framework and Point-Monitoring Demo";
  pptx.company = "pylon1";
  pptx.lang = zh ? "zh-CN" : "en-GB";
  pptx.theme = {
    headFontFace: zh ? "Microsoft YaHei" : "Aptos Display",
    bodyFontFace: zh ? "Microsoft YaHei" : "Aptos",
    lang: zh ? "zh-CN" : "en-GB",
  };

  function footer(slide, n) {
    slide.addShape(pptx.ShapeType.line, { x: 0.55, y: 7.0, w: 12.2, h: 0, line: { color: "D7E0EA", width: 0.8 } });
    slide.addText(zh ? "pylon1 galloping research | single-point demo | 2026-06-09" : "pylon1 galloping research | single-point demo | 2026-06-09", {
      x: 0.62, y: 7.1, w: 8.5, h: 0.18, fontFace: "Aptos", fontSize: 7.2, color: "7B8794"
    });
    slide.addText(String(n).padStart(2, "0"), { x: 12.35, y: 7.08, w: 0.38, h: 0.18, fontFace: "Aptos", fontSize: 8, color: "7B8794", align: "right" });
  }

  function title(slide, text, kicker) {
    if (kicker) slide.addText(kicker, { x: 0.62, y: 0.25, w: 11.8, h: 0.22, fontFace: "Aptos", fontSize: 8.6, bold: true, color: C.teal, charSpace: 0.5 });
    slide.addText(text, { x: 0.62, y: 0.55, w: 12.0, h: 0.56, fontFace: zh ? "Microsoft YaHei" : "Aptos Display", fontSize: 21.5, bold: true, color: C.ink, fit: "shrink" });
  }

  function claim(slide, text, y = 1.25) {
    slide.addShape(pptx.ShapeType.rect, { x: 0.62, y, w: 12.05, h: 0.56, fill: { color: "EAF3F8" }, line: { color: "CFE2EE", width: 0.7 } });
    slide.addText(text, { x: 0.86, y: y + 0.12, w: 11.55, h: 0.25, fontFace: zh ? "Microsoft YaHei" : "Aptos", fontSize: 12.6, bold: true, color: C.blue, fit: "shrink" });
  }

  function box(slide, x, y, w, h, head, body, color = C.blue) {
    slide.addShape(pptx.ShapeType.rect, { x, y, w, h, fill: { color: C.white }, line: { color: C.line, width: 0.8 } });
    slide.addShape(pptx.ShapeType.rect, { x, y, w: 0.08, h, fill: { color }, line: { color } });
    slide.addText(head, { x: x + 0.2, y: y + 0.12, w: w - 0.3, h: 0.25, fontFace: zh ? "Microsoft YaHei" : "Aptos", fontSize: 10.8, bold: true, color, fit: "shrink" });
    slide.addText(body, { x: x + 0.2, y: y + 0.46, w: w - 0.35, h: h - 0.55, fontFace: zh ? "Microsoft YaHei" : "Aptos", fontSize: 9.5, color: C.ink, fit: "shrink", valign: "top", breakLine: false });
  }

  function bullets(slide, items, x, y, w, h, size = 11) {
    slide.addText(items.map(t => ({ text: t, options: { bullet: { type: "bullet" }, breakLine: true } })), {
      x, y, w, h,
      fontFace: zh ? "Microsoft YaHei" : "Aptos",
      fontSize: size,
      color: C.ink,
      fit: "shrink",
      breakLine: false,
      paraSpaceAfterPt: 7,
      valign: "top",
    });
  }

  function img(slide, file, x, y, w, h) {
    slide.addImage({ path: path.join(PKG, file), x, y, w, h });
  }

  function addTable(slide, rows, x, y, w, h, colW, size = 8.2) {
    slide.addTable(rows, {
      x, y, w, h, colW,
      margin: 0.055,
      border: { type: "solid", color: C.line, pt: 0.55 },
      fontFace: zh ? "Microsoft YaHei" : "Aptos",
      fontSize: size,
      color: C.ink,
      valign: "mid",
      fit: "shrink",
      autoFit: false,
    });
  }

  let s; let n = 1;

  s = pptx.addSlide();
  s.background = { color: "F7FAFC" };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.18, fill: { color: C.blue }, line: { color: C.blue } });
  s.addText(zh ? "架空导线 Galloping 研究" : "Overhead Conductor Galloping Study", { x: 0.75, y: 0.85, w: 10.8, h: 0.34, fontFace: zh ? "Microsoft YaHei" : "Aptos", fontSize: 13, color: C.teal, bold: true });
  s.addText(zh ? "研究框架、Limits 设计与三测点范例" : "Framework, Limits Design, and Three-Point Demo", { x: 0.75, y: 1.35, w: 11.7, h: 0.68, fontFace: zh ? "Microsoft YaHei" : "Aptos Display", fontSize: 28, bold: true, color: C.ink, fit: "shrink" });
  s.addText(zh ? "保留全线时域判据，同时新增跨中和两个四分点的展示型单点监测结果" : "Line-level time-domain limits are retained; midspan and quarter-point monitors are added for interpretable demonstration.", { x: 0.78, y: 2.12, w: 11.2, h: 0.34, fontFace: zh ? "Microsoft YaHei" : "Aptos", fontSize: 13, color: C.gray, fit: "shrink" });
  box(s, 0.78, 3.1, 3.55, 1.25, zh ? "基准工况" : "Baseline Case", zh ? `L=322.8 m, H=10.48 m\nu_star=0.60 m/s, seed=${meta.case.seed}` : `L=322.8 m, H=10.48 m\nu_star=0.60 m/s, seed=${meta.case.seed}`, C.blue);
  box(s, 4.55, 3.1, 3.55, 1.25, zh ? "目标记录" : "Target Records", zh ? "4096 步, dt=0.05 s\n总时长 204.8 s" : "4096 records, dt=0.05 s\nDuration 204.8 s", C.green);
  box(s, 8.32, 3.1, 3.55, 1.25, zh ? "观测点" : "Monitors", zh ? "1/4 跨、跨中、3/4 跨\n节点 26, 51, 76" : "1/4 span, midspan, 3/4 span\nNodes 26, 51, 76", C.amber);
  footer(s, n++);

  s = pptx.addSlide(); title(s, zh ? "研究问题与当前框架" : "Research Question and Framework", "FRAMEWORK");
  claim(s, zh ? "目标不是只给出“是否 gallop”，而是建立 coverage_i(L, u_star) 形式的多判据时域响应函数。" : "The target is not a single yes/no galloping flag, but a family of time-domain coverage functions coverage_i(L, u_star).");
  box(s, 0.75, 2.15, 3.6, 1.75, zh ? "输入层" : "Inputs", zh ? "导线结构、L-H 几何、材料参数、u_star、seed" : "Conductor structure, L-H geometry, material data, u_star, seed", C.blue);
  box(s, 4.82, 2.15, 3.6, 1.75, zh ? "求解层" : "Solver Layer", zh ? "Python 风场/风荷载生成\nOpenSees 时域非线性动力响应" : "Python wind/force generation\nOpenSees time-domain nonlinear response", C.teal);
  box(s, 8.89, 2.15, 3.6, 1.75, zh ? "判据层" : "Criteria Layer", zh ? "全线 limits 计算覆盖率\n单点监测用于展示和解释" : "Line-level limits produce coverage\nPoint monitors support explanation", C.green);
  bullets(s, zh ? [
    "批量研究仍使用全线最不利节点/单元聚合的 limits，保证工程风险不被单点遗漏。",
    "本次新增单点监测只作为展示结果：解释跨中和四分点处响应、气动系数与阻尼如何随时间演化。",
    "后续扩展到多 L 和多束导线时，单点展示可以作为典型工况的诊断窗口。"
  ] : [
    "The production limits remain line-level or worst-node/element aggregates, so risk is not missed by a single monitor.",
    "The new point monitors are demonstration outputs that explain how response, coefficients, and damping evolve locally.",
    "For future span and bundle studies, this view becomes a diagnostic window for representative cases."
  ], 0.95, 4.55, 11.55, 1.35, 11.2);
  footer(s, n++);

  s = pptx.addSlide(); title(s, zh ? "范例几何与三测点" : "Example Geometry and Three Observation Points", "CASE SETUP");
  claim(s, zh ? "三测点选择跨中和两个四分点：既覆盖最大垂度位置，也覆盖可能出现非对称局部响应的两侧区域。" : "The three monitors cover the maximum-sag position and the two side regions where asymmetric local behaviour may appear.");
  img(s, "monitor_points_geometry.png", 0.78, 2.0, 7.0, 3.05);
  addTable(s, [
    [{ text: zh ? "位置" : "Location", options: { bold: true, fill: C.pale } }, { text: "Node", options: { bold: true, fill: C.pale } }, { text: "x/L", options: { bold: true, fill: C.pale } }, { text: zh ? "相邻单元" : "Adjacent elements", options: { bold: true, fill: C.pale } }],
    ["1/4", "26", "0.25", "25, 26"],
    [zh ? "跨中" : "Midspan", "51", "0.50", "50, 51"],
    ["3/4", "76", "0.75", "75, 76"],
  ], 8.15, 2.25, 4.3, 1.35, [1.25, 0.8, 0.8, 1.45], 8.5);
  box(s, 8.15, 4.15, 4.3, 1.35, zh ? "方向说明" : "Direction Note", zh ? "图中的 x 位移是风-振平面水平向，对应 OpenSees 第 2 自由度；z 是竖向，第 3 自由度。OpenSees 第 1 自由度为跨向坐标。" : "The plotted x response is the horizontal wind-vibration direction, corresponding to OpenSees DOF 2. z is the vertical DOF 3; DOF 1 is spanwise.", C.amber);
  footer(s, n++);

  s = pptx.addSlide(); title(s, zh ? "Limits 如何设置：保留全线判据" : "How the Limits Are Defined: Line-Level Criteria Retained", "LIMITS");
  claim(s, zh ? "单点监测不替代 limits；limits 仍在全线节点/单元上按每个时间步筛选，并计算覆盖率。" : "Point monitoring does not replace the limits; the limits are still evaluated over the full line at every time step.");
  addTable(s, [
    [{ text: "Limit", options: { bold: true, fill: C.pale } }, { text: zh ? "含义" : "Meaning", options: { bold: true, fill: C.pale } }, { text: zh ? "当前时域规则" : "Current time-domain rule", options: { bold: true, fill: C.pale } }, { text: zh ? "为什么用" : "Why it is used", options: { bold: true, fill: C.pale } }],
    ["C2", zh ? "负有效阻尼" : "Negative effective damping", zh ? "单元 xi_total 出现显著负值且达到元素比例阈值" : "A meaningful fraction of elements has negative xi_total", zh ? "对应 Den Hartog 型自激机制的 onset 信号" : "Onset signal for Den Hartog-type self-excitation"],
    ["C4", zh ? "响应增长" : "Response growth", zh ? "全线最大位移的 20 s rolling p95 增长" : "20 s rolling p95 growth of line-level maximum displacement", zh ? "识别随机振动之外的持续放大过程" : "Captures sustained growth beyond random vibration"],
    ["C6", zh ? "大响应" : "Large response", zh ? "全线最大位移 >= 0.10 H" : "Line-level maximum displacement >= 0.10 H", zh ? "代表已发展为工程上可见的大幅响应" : "Marks a developed, visible large-response state"],
    ["C2&C4", zh ? "机制与增长同步" : "Mechanism and growth coincide", zh ? "同一时间步 C2 和 C4 同时成立" : "C2 and C4 are true at the same time step", zh ? "比单独 C2 更严格，避免只看瞬时负阻尼" : "Stricter than C2 alone; avoids isolated damping events"],
    ["C7", zh ? "工程后果通道" : "Engineering consequence channel", zh ? "净空/相间距/张力等 limit-state 占位" : "Clearance, phase spacing, or tension limit-state placeholder", zh ? "保留工程规范接口，但仍需真实净空校准" : "Keeps the code-based consequence channel; needs calibration"],
  ], 0.55, 2.05, 12.25, 4.15, [0.75, 2.0, 4.7, 4.8], 7.2);
  footer(s, n++);

  s = pptx.addSlide(); title(s, zh ? "Limits 的文献和机理依据" : "Mechanistic and Literature Basis for the Limits", "EVIDENCE");
  claim(s, zh ? "这些 limits 不是任意阈值，而是把 galloping 的机理、响应发展和工程后果分开记录。" : "The limits are not arbitrary thresholds; they separate galloping mechanism, response development, and engineering consequence.");
  box(s, 0.72, 2.05, 3.7, 2.0, zh ? "Den Hartog / 课件" : "Den Hartog / Lecture", zh ? "气动力斜率可表现为负气动阻尼。C2 用 xi_total < 0 记录自激机制是否出现。" : "Aerodynamic force slope can behave as negative damping. C2 records whether this self-exciting mechanism appears.", C.blue);
  box(s, 4.82, 2.05, 3.7, 2.0, zh ? "Rossi 等与 galloping 文献" : "Rossi et al. and Galloping Literature", zh ? "Den Hartog 条件是必要筛选，不等于一定发生大幅 galloping；因此需要 C4/C6 记录响应发展。" : "Den Hartog susceptibility is a necessary screening signal, not a full large-response guarantee; C4/C6 track development.", C.green);
  box(s, 8.92, 2.05, 3.7, 2.0, zh ? "EN 50341 / RICA 接口" : "EN 50341 / RICA Interface", zh ? "工程设计关心净空、相间距和 clashing 风险。C7 保留该接口，但暂不作为主结论。" : "Engineering design cares about clearance, phase spacing, and clashing. C7 preserves this interface but is not yet the primary conclusion.", C.amber);
  bullets(s, zh ? [
    "C2 是机理层：问“是否具备自激条件”。",
    "C4 是过程层：问“响应是否正在持续增长”。",
    "C6 是状态层：问“是否已经达到显著大幅响应”。",
    "C7 是后果层：问“是否触及工程净空或相间距限制”。"
  ] : [
    "C2 is the mechanism layer: is self-excitation present?",
    "C4 is the process layer: is the response growing persistently?",
    "C6 is the state layer: has a significant large response developed?",
    "C7 is the consequence layer: are clearance or spacing limits reached?"
  ], 1.0, 4.78, 11.2, 1.2, 11.1);
  footer(s, n++);

  s = pptx.addSlide(); title(s, zh ? "单点范例结果：水平 x 位移" : "Point-Monitoring Result: Horizontal x Displacement", "RESULT 1");
  claim(s, zh ? "三个观测点均在约 135 s 后出现明显增长；跨中的水平向幅值最大。" : "All three monitors show clear growth after about 135 s; the midspan monitor has the largest horizontal amplitude.");
  img(s, "displacement_x_timeseries.png", 0.72, 1.95, 11.9, 4.65);
  footer(s, n++);

  s = pptx.addSlide(); title(s, zh ? "单点范例结果：竖向 z 位移" : "Point-Monitoring Result: Vertical z Displacement", "RESULT 2");
  claim(s, zh ? "竖向响应更直观地展示了从小幅随机振动到大幅响应的窗口化发展过程。" : "The vertical response clearly shows the windowed transition from small random vibration to large response.");
  img(s, "displacement_z_timeseries.png", 0.72, 1.95, 11.9, 4.65);
  footer(s, n++);

  s = pptx.addSlide(); title(s, zh ? "单点范例结果：C_D 与 C_L" : "Point-Monitoring Result: C_D and C_L", "RESULT 3");
  claim(s, zh ? "C_D/C_L 来自同一风场角度查表，说明风荷载输入随局部攻角连续更新，而不是固定系数。" : "C_D/C_L are table-interpolated from the same local wind angle, showing that the aerodynamic load updates continuously rather than using fixed coefficients.");
  img(s, "cd_timeseries.png", 0.65, 2.0, 5.95, 4.25);
  img(s, "cl_timeseries.png", 6.75, 2.0, 5.95, 4.25);
  footer(s, n++);

  s = pptx.addSlide(); title(s, zh ? "单点范例结果：有效阻尼记录" : "Point-Monitoring Result: Effective Damping Records", "RESULT 4");
  claim(s, zh ? "阻尼是相邻单元层面的记录；负阻尼窗口解释了为什么 C2 是 onset 机制信号，而不是单独的大响应判据。" : "Damping is recorded at adjacent elements; negative-damping windows explain why C2 is an onset mechanism signal rather than a standalone large-response criterion.");
  img(s, "damping_timeseries.png", 0.72, 1.95, 8.25, 4.65);
  box(s, 9.25, 2.15, 3.1, 1.2, zh ? "记录方式" : "Recording", zh ? "Damping_shifter.tcl\n每 20 个增量记录一次\n列：time, element, prev_xi, xi_total" : "Damping_shifter.tcl\nlogged every 20 increments\ncolumns: time, element, prev_xi, xi_total", C.teal);
  box(s, 9.25, 3.7, 3.1, 1.35, zh ? "单点映射" : "Point Mapping", zh ? "节点阻尼用相邻两个单元的 xi_total 均值展示；全线 C2 仍使用全部单元聚合。" : "Point damping is shown as the mean xi_total of the two adjacent elements; line-level C2 still aggregates all elements.", C.amber);
  footer(s, n++);

  s = pptx.addSlide(); title(s, zh ? "三测点统计摘要" : "Three-Monitor Summary", "SUMMARY");
  claim(s, zh ? "该表格用于会议展示与诊断；研究判据仍以全线时域覆盖率为主。" : "This table supports presentation and diagnosis; the research criteria still rely on line-level time-domain coverage.");
  const tableRows = [
    [{ text: zh ? "位置" : "Point", options: { bold: true, fill: C.pale } }, { text: "Node", options: { bold: true, fill: C.pale } }, { text: zh ? "max |x| m" : "max |x| m", options: { bold: true, fill: C.pale } }, { text: zh ? "max |z| m" : "max |z| m", options: { bold: true, fill: C.pale } }, { text: zh ? "mean C_D" : "mean C_D", options: { bold: true, fill: C.pale } }, { text: zh ? "min xi" : "min xi", options: { bold: true, fill: C.pale } }, { text: zh ? "负阻尼比例" : "neg. xi frac.", options: { bold: true, fill: C.pale } }],
  ];
  summary.forEach((r) => {
    tableRows.push([
      zh ? r.monitor.replace("Midspan", "跨中").replace("span", "跨") : r.monitor,
      r.node,
      fmt(r.max_abs_disp_x_m, 3),
      fmt(r.max_abs_disp_z_m, 3),
      fmt(r.mean_C_D, 3),
      fmt(r.min_xi, 3),
      fmt(r.negative_xi_fraction_recorded, 3),
    ]);
  });
  addTable(s, tableRows, 0.65, 2.0, 12.05, 1.65, [1.65, 0.7, 1.35, 1.35, 1.2, 1.1, 1.45], 8.2);
  bullets(s, zh ? [
    "跨中节点 51 的竖向响应最大，符合最大垂度位置更易呈现大幅位移的直觉。",
    "3/4 点附近的记录负阻尼比例较高，说明局部气动阻尼窗口可能具有非对称性。",
    "这些单点图适合会议解释；最终 L-u_star 风险函数仍应由 C2/C4/C6/C2&C4/C7 的全线覆盖率曲线和曲面给出。"
  ] : [
    "Midspan node 51 has the largest vertical response, consistent with the maximum-sag location being more displacement-sensitive.",
    "The 3/4-span monitor has a higher recorded negative-damping fraction, suggesting local aerodynamic damping windows can be asymmetric.",
    "These point plots are useful for explanation; the final L-u_star risk function should still come from line-level C2/C4/C6/C2&C4/C7 coverage curves and surfaces."
  ], 0.9, 4.2, 11.6, 1.25, 11.2);
  footer(s, n++);

  const outName = zh ? "Galloping_Single_Point_Demo_CN.pptx" : "Galloping_Single_Point_Demo_EN.pptx";
  return pptx.writeFile({ fileName: path.join(OUT, outName) });
}

Promise.resolve()
  .then(() => deck("zh"))
  .then(() => deck("en"))
  .then(() => {
    console.log(JSON.stringify({
      output_dir: OUT,
      decks: [
        path.join(OUT, "Galloping_Single_Point_Demo_CN.pptx"),
        path.join(OUT, "Galloping_Single_Point_Demo_EN.pptx")
      ]
    }, null, 2));
  })
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
