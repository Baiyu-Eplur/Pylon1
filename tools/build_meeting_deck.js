const fs = require("fs");
const path = require("path");
const PptxGenJS = require("C:/Users/haoya/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/pptxgenjs/dist/pptxgen.cjs.js");

const ROOT = "D:/Pyprogramme/pylon1";
const OUT_DIR = path.join(ROOT, "output", "reports", "galloping_meeting_deck");
const PKG = path.join(ROOT, "output", "time_step_coverage_audit", "L300_350_400_ustar_grid_n4096_s3_plus_extra", "result_package");
const PPTX_PATH = path.join(OUT_DIR, "Galloping_Research_Framework_Workflow_Limits_Meeting.pptx");
const NOTES_PATH = path.join(OUT_DIR, "Galloping_Research_Framework_Workflow_Limits_Speaker_Notes.md");

fs.mkdirSync(OUT_DIR, { recursive: true });

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "pylon1 galloping research workflow";
pptx.subject = "Overhead conductor galloping: framework, workflow, and limits design";
pptx.title = "Galloping Research Framework, Workflow, and Limits";
pptx.company = "University of Birmingham / pylon1";
pptx.lang = "zh-CN";
pptx.theme = {
  headFontFace: "Microsoft YaHei",
  bodyFontFace: "Microsoft YaHei",
  lang: "zh-CN",
};
pptx.defineLayout({ name: "CUSTOM_WIDE", width: 13.333, height: 7.5 });
pptx.layout = "CUSTOM_WIDE";
pptx.margin = 0;

const C = {
  navy: "1F4D78",
  blue: "2E74B5",
  cyan: "0E7C86",
  green: "4A8F5A",
  red: "B24A4A",
  amber: "C7832B",
  ink: "20242A",
  gray: "5D6773",
  pale: "F4F7FB",
  line: "B7C9DD",
  white: "FFFFFF",
};

function addFooter(slide, n, source = "pylon1 simulation records | updated 2026-06-09") {
  slide.addText(source, { x: 0.55, y: 7.08, w: 9.2, h: 0.18, fontFace: "Calibri", fontSize: 6.8, color: "7B8794" });
  slide.addText(String(n).padStart(2, "0"), { x: 12.45, y: 7.02, w: 0.35, h: 0.2, fontFace: "Calibri", fontSize: 8, color: "7B8794", align: "right" });
}

function title(slide, text, kicker) {
  if (kicker) slide.addText(kicker, { x: 0.55, y: 0.28, w: 11.5, h: 0.22, fontFace: "Calibri", fontSize: 8.5, color: C.cyan, bold: true, charSpace: 0.4 });
  slide.addText(text, { x: 0.55, y: 0.55, w: 12.1, h: 0.5, fontFace: "Microsoft YaHei", fontSize: 22, bold: true, color: C.ink, fit: "shrink" });
  slide.addShape(pptx.ShapeType.line, { x: 0.55, y: 1.18, w: 12.15, h: 0, line: { color: "D6DEE8", width: 1 } });
}

function addClaim(slide, text, y = 1.34) {
  slide.addShape(pptx.ShapeType.rect, { x: 0.62, y, w: 12.0, h: 0.58, fill: { color: "EAF3F8" }, line: { color: "CFE2EE", width: 0.8 }, radius: 0.08 });
  slide.addText(text, { x: 0.85, y: y + 0.11, w: 11.55, h: 0.32, fontFace: "Microsoft YaHei", fontSize: 14, bold: true, color: C.navy, fit: "shrink" });
}

function addBullets(slide, items, x, y, w, h, opts = {}) {
  const runs = items.map((t) => ({ text: t, options: { bullet: { type: "bullet" }, breakLine: true } }));
  slide.addText(runs, {
    x, y, w, h,
    fontFace: "Microsoft YaHei",
    fontSize: opts.fontSize || 12,
    color: opts.color || C.ink,
    breakLine: false,
    paraSpaceAfterPt: opts.after || 7,
    fit: "shrink",
    valign: "top",
  });
}

function box(slide, x, y, w, h, label, body, fill = "F6F8FB", accent = C.blue) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.05, fill: { color: fill }, line: { color: "D6DEE8", width: 0.8 } });
  slide.addShape(pptx.ShapeType.rect, { x, y, w: 0.08, h, fill: { color: accent }, line: { color: accent } });
  slide.addText(label, { x: x + 0.18, y: y + 0.12, w: w - 0.3, h: 0.25, fontFace: "Microsoft YaHei", fontSize: 10.5, bold: true, color: accent, fit: "shrink" });
  slide.addText(body, { x: x + 0.18, y: y + 0.46, w: w - 0.3, h: h - 0.55, fontFace: "Microsoft YaHei", fontSize: 9.5, color: C.ink, fit: "shrink", valign: "top" });
}

function table(slide, rows, x, y, w, h, colW, fontSize = 8.2) {
  slide.addTable(rows, {
    x, y, w, h,
    colW,
    margin: 0.06,
    border: { type: "solid", color: C.line, pt: 0.55 },
    fontFace: "Microsoft YaHei",
    fontSize,
    color: C.ink,
    valign: "mid",
    fit: "shrink",
    autoFit: false,
  });
}

function img(slide, filename, x, y, w, h) {
  slide.addImage({ path: path.join(PKG, filename), x, y, w, h });
}

const notes = [];
function addNotes(slideNo, heading, body) {
  notes.push(`## Slide ${slideNo}. ${heading}\n\n${body.trim()}\n`);
}

let s, n = 1;

s = pptx.addSlide();
s.background = { color: "F7FAFD" };
s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 7.5, fill: { color: "F7FAFD" }, line: { color: "F7FAFD" } });
s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.18, fill: { color: C.navy }, line: { color: C.navy } });
s.addText("Overhead Conductor Galloping Study", { x: 0.65, y: 0.82, w: 10.8, h: 0.42, fontFace: "Calibri", fontSize: 13, color: C.cyan, bold: true });
s.addText("研究框架、工作流与 limits 设计", { x: 0.65, y: 1.35, w: 10.5, h: 0.65, fontFace: "Microsoft YaHei", fontSize: 29, bold: true, color: C.ink, fit: "shrink" });
s.addText("基于 L-u_star 参数化 OpenSees 时程模拟的 galloping 覆盖率研究", { x: 0.67, y: 2.12, w: 10.9, h: 0.34, fontFace: "Microsoft YaHei", fontSize: 14, color: C.gray });
box(s, 0.78, 3.05, 3.55, 1.15, "核心问题", "导线跨距 L 与风强度 u_star 如何共同影响 galloping 风险？", "FFFFFF", C.blue);
box(s, 4.55, 3.05, 3.55, 1.15, "核心方法", "把判据落到每个时间步，得到 coverage(L,u_star)，而不是只给二值结论。", "FFFFFF", C.cyan);
box(s, 8.32, 3.05, 3.55, 1.15, "核心交付", "多判据覆盖率曲面：C2、C4、C6、C2&C4、C7 和 failed fraction。", "FFFFFF", C.green);
s.addText("Meeting material | 2026-06-09", { x: 0.67, y: 6.72, w: 5.5, h: 0.22, fontFace: "Calibri", fontSize: 9, color: "8A96A3" });
addFooter(s, n++);
addNotes(1, "标题页", "开场时强调：这不是一个单纯的数值模拟展示，而是一个逐步建立 galloping 二维响应函数的研究框架。自变量是 L 和 u_star，输出不是单一临界点，而是不同判据的时域覆盖率。");

s = pptx.addSlide(); title(s, "本次汇报的主线", "EXECUTIVE SUMMARY");
addClaim(s, "我们当前最重要的进展：把 galloping 判定从“发生/不发生”升级为“多判据时域覆盖率曲面”。");
box(s, 0.72, 2.2, 3.8, 2.1, "为什么要这样做", "galloping 在随机风场下可能只在部分时段出现；近边界状态并不稳定地保持全程。因此覆盖率比单一临界区间更能反映趋势。", "FFFFFF", C.blue);
box(s, 4.78, 2.2, 3.8, 2.1, "当前最稳健的信号", "C6 大响应随 u_star 升高呈现最清晰趋势；failed fraction 反映强非线性或非正常终止风险。", "FFFFFF", C.green);
box(s, 8.84, 2.2, 3.8, 2.1, "需要谨慎解释的信号", "C2 是机制指标，不是严重程度曲线；C4 受随机 realization 影响；C7 尚未用真实工程净空重新校准。", "FFFFFF", C.amber);
addBullets(s, [
  "研究对象：Zebra ACSR 架空导线，跨距 L = 300/350/400 m。",
  "风输入：u_star = 0.30, 0.40, 0.50, 0.60, 0.80, 1.00 m/s。",
  "最新数据：64 planned cases；48 completed；16 failed/non-normal。",
], 0.95, 4.85, 11.6, 1.25, { fontSize: 11.5 });
addFooter(s, n++);
addNotes(2, "本次汇报的主线", "这一页用来给听众一个提前框架：第一，我们在做二维函数，不是单一风速临界值；第二，C6 是目前最强的结果信号；第三，C2/C4/C7 各有不同含义，不能混在一起。");

s = pptx.addSlide(); title(s, "研究问题：从临界点到覆盖率曲面", "RESEARCH QUESTION");
addClaim(s, "目标函数从 u_star,crit(L) 扩展为 coverage_i(L, u_star)：不同判据形成不同风险曲面。");
s.addText("传统问法", { x: 0.75, y: 2.05, w: 2.5, h: 0.25, fontFace: "Microsoft YaHei", fontSize: 13, bold: true, color: C.red });
s.addText("某个风速下是否发生 galloping？", { x: 0.75, y: 2.5, w: 4.0, h: 0.48, fontFace: "Microsoft YaHei", fontSize: 17, bold: true, color: C.ink });
s.addText("问题：随机风场中，响应可能只在窗口中出现；不同判据触发顺序也不同。", { x: 0.75, y: 3.15, w: 4.1, h: 0.88, fontFace: "Microsoft YaHei", fontSize: 11, color: C.gray, fit: "shrink" });
s.addShape(pptx.ShapeType.rightArrow, { x: 5.15, y: 2.72, w: 1.25, h: 0.55, fill: { color: "D7E7F3" }, line: { color: "D7E7F3" } });
s.addText("当前问法", { x: 6.75, y: 2.05, w: 2.5, h: 0.25, fontFace: "Microsoft YaHei", fontSize: 13, bold: true, color: C.green });
s.addText("200 s 中有多少时间步满足某个 limit？", { x: 6.75, y: 2.5, w: 5.3, h: 0.48, fontFace: "Microsoft YaHei", fontSize: 17, bold: true, color: C.ink, fit: "shrink" });
s.addText("coverage_fraction = problem_time_steps / total_time_steps", { x: 6.75, y: 3.14, w: 5.5, h: 0.34, fontFace: "Consolas", fontSize: 12, color: C.navy });
s.addText("优点：可以比较 C2/C4/C6/C7 的覆盖范围、保守性和物理含义。", { x: 6.75, y: 3.62, w: 5.5, h: 0.48, fontFace: "Microsoft YaHei", fontSize: 11, color: C.gray });
box(s, 0.95, 5.02, 11.35, 0.9, "最终研究形态", "coverage_Ci(L, u_star, cable_structure) 以及由 iso-coverage 推导的临界边界，例如 C6 = 50% 或 failed_fraction = 20%。", "F8FBFF", C.cyan);
addFooter(s, n++);
addNotes(3, "研究问题", "这里重点说明为什么我们没有直接去找一个单一临界风速。对于随机风和非线性导线，galloping 可以是窗口化的，因此 coverage 的概念更自然。后续如果需要临界边界，可以在曲面上取等值线。");

s = pptx.addSlide(); title(s, "总体研究框架", "FRAMEWORK");
addClaim(s, "框架分为四层：几何与材料、风场生成、OpenSees 时程模拟、判据覆盖率后处理。");
const steps = [
  ["1 几何/材料", "L, H, Zebra ACSR\nw=15.90 N/m\nT0=19.785 kN", C.blue],
  ["2 风场/荷载", "u_star log-law\nKaimal spectra\nDavenport coherence", C.cyan],
  ["3 时程模拟", "OpenSees TH\n位移/加速度/反力\nxi_total damping log", C.green],
  ["4 Limits 后处理", "C2/C4/C6/C7\nC2&C4\nfailed fraction", C.amber],
];
for (let i = 0; i < steps.length; i++) {
  const [lab, body, color] = steps[i];
  const x = 0.65 + i * 3.13;
  box(s, x, 2.1, 2.62, 2.05, lab, body, "FFFFFF", color);
  if (i < steps.length - 1) s.addShape(pptx.ShapeType.rightArrow, { x: x + 2.68, y: 2.9, w: 0.42, h: 0.35, fill: { color: "CAD7E6" }, line: { color: "CAD7E6" } });
}
addBullets(s, [
  "同一统计气象生成框架：相同 roughness、log-law、谱模型、相干模型和时间步设置。",
  "不同 L 会改变节点位置、节点高度和相干距离，因此这是 common statistical weather scenario，不是完全相同的风时程。",
  "不同 seed 用于估计随机 realization 下的覆盖率变化。"
], 0.95, 4.78, 11.3, 1.25, { fontSize: 11.2 });
addFooter(s, n++);
addNotes(4, "总体研究框架", "这一页可以解释模型链路：我们先确定 L-H 和导线物理参数，再由 u_star 生成风场和荷载，之后让 OpenSees 产生时域响应，最后把 limits 应用到每个时间步。注意要讲清 common weather scenario 是统计意义。");

s = pptx.addSlide(); title(s, "几何与风场设置", "MODEL SETUP");
addClaim(s, "为了比较 L 的影响，每个跨距都用同一导线和同一初拉力规则重新匹配 H。");
table(s, [
  [{ text: "L (m)", options: { bold: true, fill: C.pale } }, { text: "H/Sag (m)", options: { bold: true, fill: C.pale } }, { text: "H/L", options: { bold: true, fill: C.pale } }, { text: "匹配逻辑", options: { bold: true, fill: C.pale } }],
  ["300", "9.041", "0.030", "H = wL²/(8T0)"],
  ["350", "12.306", "0.035", "同一 w 与 T0"],
  ["400", "16.073", "0.040", "parabolic_tension"],
], 0.75, 2.0, 5.65, 1.55, [1.1, 1.3, 0.9, 2.35], 8.8);
box(s, 6.85, 1.95, 5.65, 1.55, "风速参数化", "u_star = 0.30, 0.40, 0.50, 0.60, 0.80, 1.00 m/s\nU(z)=u_star/0.387·log(z/0.05)", "FFFFFF", C.cyan);
box(s, 0.75, 4.28, 5.65, 1.35, "时间窗口", "npt = 4096, dt = 0.05 s, duration = 204.8 s\n审计固定前 4096 条目标记录，避免自适应子步偏置。", "FFFFFF", C.green);
box(s, 6.85, 4.28, 5.65, 1.35, "随机 realization", "每个格点至少 3 个 seed；高失败格点补 2 个 seed。\n最新数据：64 planned / 48 completed / 16 non-normal。", "FFFFFF", C.amber);
addFooter(s, n++);
addNotes(5, "几何与风场设置", "强调 H 不是随意取的，而是使用导线自重和初拉力匹配。风速自变量是 u_star，而不是直接输入节点力。每个 case 都重新生成与几何匹配的风荷载。");

s = pptx.addSlide(); title(s, "工作流：从原始工程到可批量扫描", "WORKFLOW");
addClaim(s, "关键不是单次算例，而是把 MATLAB 风场逻辑、OpenSees 时程和判据审计连成可重复 pipeline。");
const wf = [
  ["MATLAB 溯源", "WIND_SIMULATION.mlx\nfriction-based u_star 逻辑"],
  ["Python 移植", "wind_forces.py\nforce/wind metadata"],
  ["模型校验", "线形、质量、刚度、模态\n动态风响应"],
  ["批量生成", "run_l_ustar_sweep.py\nL-u_star-seed grid"],
  ["时域审计", "time_step_coverage_audit.py\nmax-records=4096"],
  ["聚合出图", "aggregate + result package\nsurface/table/report"],
];
for (let i = 0; i < wf.length; i++) {
  const row = i < 3 ? 0 : 1;
  const col = i % 3;
  box(s, 0.75 + col * 4.05, 1.85 + row * 2.05, 3.35, 1.25, wf[i][0], wf[i][1], "FFFFFF", [C.blue, C.cyan, C.green, C.amber, C.red, C.navy][i]);
}
addBullets(s, [
  "风荷载不是简单放大现有 force，而是按 u_star、几何、seed 重新生成。",
  "失败案例被审计为 non-normal dynamic termination，不作为前处理错误删除。",
], 1.0, 6.1, 11.3, 0.65, { fontSize: 10.6, after: 3 });
addFooter(s, n++);
addNotes(6, "工作流", "这里重点讲工程可信度：我们不是临时拼脚本，而是已经把风荷载生成、时程模拟、后处理和出图打通。尤其要强调力来自原始 MATLAB 工程逻辑的移植。");

s = pptx.addSlide(); title(s, "Limits 设计原则：不要把所有标准取交集", "LIMIT DESIGN PRINCIPLE");
addClaim(s, "物理机制、响应表现、工程后果是三类不同证据；本阶段必须分别记录。");
box(s, 0.72, 2.0, 3.65, 2.1, "机制层", "C1/C2\nDen Hartog susceptibility\n有效总阻尼为负", "FFFFFF", C.blue);
box(s, 4.85, 2.0, 3.65, 2.1, "响应层", "C4/C5/C6\n幅值增长\n低频大幅响应\n进入强非线性", "FFFFFF", C.green);
box(s, 8.98, 2.0, 3.65, 2.1, "后果层", "C7\n相间距/净空/张力\n工程 limit-state", "FFFFFF", C.amber);
s.addShape(pptx.ShapeType.line, { x: 2.55, y: 4.35, w: 8.1, h: 0, line: { color: "CAD7E6", width: 1.2, beginArrowType: "none", endArrowType: "triangle" } });
s.addText("从 onset 机制 → 可观测响应 → 工程后果", { x: 3.95, y: 4.52, w: 5.9, h: 0.26, fontFace: "Microsoft YaHei", fontSize: 12, color: C.navy, bold: true, align: "center" });
addBullets(s, [
  "如果直接取交集，会丢失近边界窗口、seed 敏感性和工程后果差异。",
  "每个 limit 单独形成 coverage_i(L,u_star)，之后再比较保守性和覆盖范围。",
  "最终临界边界应来自 iso-coverage，而不是单次 whole-record binary flag。"
], 1.0, 5.25, 11.2, 1.0, { fontSize: 11.3 });
addFooter(s, n++);
addNotes(7, "Limits 设计原则", "这一页是汇报重点。要明确我们不把所有判据合成一个 yes/no，因为 Den Hartog 机制、动态响应和工程 limit-state 不是同一件事。这样设计的好处是每个标准都能保留自己的物理意义。");

s = pptx.addSlide(); title(s, "Limits 具体如何设置", "CURRENT TIME-DOMAIN LIMITS");
addClaim(s, "所有 limits 都落到时间步：一个 204.8 s 工况中，有多少时间步满足该标准。");
table(s, [
  [{ text: "Limit", options: { bold: true, fill: C.pale } }, { text: "判定对象", options: { bold: true, fill: C.pale } }, { text: "当前规则", options: { bold: true, fill: C.pale } }, { text: "解释", options: { bold: true, fill: C.pale } }],
  ["C2", "有效负阻尼", "xi_total < 0 且达到持续/比例阈值", "incipient mechanism"],
  ["C4", "响应增长", "20 s rolling p95 displacement growth", "growth process"],
  ["C6", "大响应", "displacement >= 0.10 × Sag", "developed response"],
  ["C2&C4", "同步证据", "同一时间步 C2 与 C4 同时成立", "strict marker"],
  ["C7", "工程后果", "clearance/tension proxy", "未校准，不作主结论"],
  ["Failed", "非正常终止", "OpenSees non-zero / incomplete final row", "辅助失稳曲面"],
], 0.55, 1.72, 12.25, 4.25, [0.85, 1.8, 4.3, 5.3], 7.5);
addCalloutText = "当前主结果中，C6 是最清晰的 developed-response 曲面；C7 因未按真实净空重新校准，只作为通道保留。";
s.addShape(pptx.ShapeType.roundRect, { x: 0.72, y: 6.15, w: 11.9, h: 0.55, rectRadius: 0.05, fill: { color: "FFF7E8" }, line: { color: "E7C27A", width: 0.8 } });
s.addText(addCalloutText, { x: 0.95, y: 6.29, w: 11.45, h: 0.22, fontFace: "Microsoft YaHei", fontSize: 10.8, color: C.ink, bold: true, fit: "shrink" });
addFooter(s, n++);
addNotes(8, "Limits 具体如何设置", "逐个解释：C2 不是位移，而是阻尼机制；C4 是响应增长过程；C6 是大响应状态；C2&C4 是严格同步；C7 是工程后果但还没校准；失败率是数值/动力强非线性风险，不删掉。");

s = pptx.addSlide(); title(s, "为什么这样设置：文献与标准依据", "EVIDENCE BASE");
addClaim(s, "每个 limit 都对应文献中的一类证据：气动负阻尼、响应增长、强非线性大幅运动、工程限值。");
table(s, [
  [{ text: "依据", options: { bold: true, fill: C.pale } }, { text: "支持的设置", options: { bold: true, fill: C.pale } }, { text: "在本研究中的作用", options: { bold: true, fill: C.pale } }],
  ["Week 7 lecture / Den Hartog", "运动相关气动力等效为气动阻尼；总阻尼为负会产生增长", "支持 C1/C2 作为 onset 机制层"],
  ["Rossi et al. 2020", "Den Hartog 是必要筛选；实际发生还需总阻尼/响应达到条件", "支持 C2 与 C4/C6 分离"],
  ["Chabart & Lilien 1998", "风洞中存在 limit cycle、高幅响应和 Den-Hartog unstable ranges", "支持 C6 与失败/非正常终止作为强响应证据"],
  ["Zulli/Piccardo/Luongo; Ferretti et al.", "浅弧垂导线 galloping 需要稳定性与非线性响应框架", "支持未来 C8/eigen boundary"],
  ["EN 50341 / National Grid RICA", "净空、相间距、galloping ellipse 和 clashing 是工程后果", "支持 C7，但必须与物理 onset 分离"],
  ["IEC 60826 / EN 50182", "导线强度、可靠度、机械数据一致性", "支持 metadata 和工程 limit-state 通道"],
], 0.62, 1.75, 12.05, 4.65, [3.0, 4.4, 4.65], 7.35);
addBullets(s, [
  "一句话：C2 解释为什么会自激，C4/C6 解释是否发展成可观测 galloping，C7 解释是否构成工程后果。",
], 0.9, 6.42, 11.6, 0.35, { fontSize: 10.5, after: 0 });
addFooter(s, n++);
addNotes(9, "文献与标准依据", "会议中这一页用来回答“limits 凭什么这么设”。Den Hartog/Week7 给 C2；Rossi 强调必要但不充分；Chabart & Lilien 支持大幅响应和 limit-cycle；EN50341/RICA 给工程后果但不是物理 onset。");

s = pptx.addSlide(); title(s, "实验矩阵与数据可信度", "EXPERIMENT MATRIX");
addClaim(s, "补样不是为了让曲线更好看，而是为了高失败格点的可信度。");
table(s, [
  [{ text: "数据项", options: { bold: true, fill: C.pale } }, { text: "当前设置/结果", options: { bold: true, fill: C.pale } }],
  ["跨距 L", "300, 350, 400 m"],
  ["下垂 H", "9.041, 12.306, 16.073 m"],
  ["u_star", "0.30, 0.40, 0.50, 0.60, 0.80, 1.00 m/s"],
  ["时程长度", "4096 records × 0.05 s = 204.8 s"],
  ["样本数量", "64 planned / 48 completed / 16 failed or non-normal"],
  ["补样格点", "L300-U0.80; L350-U0.80/U1.00; L400-U0.50/U0.80"],
], 0.82, 1.82, 5.65, 3.15, [1.75, 3.9], 8.5);
box(s, 7.0, 1.82, 5.35, 1.25, "失败率最高格点", "L=300,u=0.80: 60%\nL=350,u=0.80/1.00: 60%\nL=400,u=0.50/0.80: 40%", "FFFFFF", C.red);
box(s, 7.0, 3.42, 5.35, 1.25, "失败原因解释", "不是缺输入或风场生成失败；而是进入强非线性响应后 OpenSees 非正常终止，Dynamic.out 最后一行不完整。", "FFFFFF", C.amber);
box(s, 7.0, 5.02, 5.35, 0.85, "处理方式", "不纳入 completed-case coverage 平均，但作为 failed_fraction(L,u_star) 单独报告。", "FFFFFF", C.green);
addFooter(s, n++);
addNotes(10, "实验矩阵与可信度", "这一页解释为什么有失败案例以及我们怎么处理。强调失败案例不是软件前处理错误，而是强响应状态下的非正常动力终止，因此应该作为风险信号的一部分。");

s = pptx.addSlide(); title(s, "结果总览：按几何构型的覆盖率表", "RESULTS");
addClaim(s, "C6 随 u_star 升高最清晰；C4 非单调但反映增长过程；C2&C4 保守。");
img(s, "coverage_tables_all_geometries.png", 0.65, 1.48, 12.05, 5.25);
addFooter(s, n++);
addNotes(11, "覆盖率表", "这里不要逐格念数字。重点点出三个趋势：第一，C6 在 0.5-0.8 后明显升高；第二，C4 有波动，说明增长过程受随机风和窗口影响；第三，C2&C4 数值小，因为它要求同一时间步机制和响应同时成立。");

s = pptx.addSlide(); title(s, "二维曲面：developed response 与 growth process", "SURFACES");
addClaim(s, "C6 是当前最适合作为主 developed-response surface 的判据；C4 保留为增长过程指标。");
img(s, "C6_large_response_surface.png", 0.75, 1.65, 5.75, 3.6);
img(s, "C4_growth_surface.png", 6.85, 1.65, 5.75, 3.6);
box(s, 0.95, 5.72, 5.3, 0.72, "C6 解读", "覆盖率在 u_star≈0.50-0.60 后迅速升高，反映进入大幅响应区。", "FFFFFF", C.green);
box(s, 7.05, 5.72, 5.3, 0.72, "C4 解读", "非单调但重要；它捕捉增长过程，而不是最终幅值。", "FFFFFF", C.cyan);
addFooter(s, n++);
addNotes(12, "C6 和 C4 曲面", "这一页是结果核心。C6 看起来最像我们想要的风险函数；C4 则更像过程证据。C4 不单调并不是失败，而是在随机风和非线性平台下合理。");

s = pptx.addSlide(); title(s, "机制与保守交集：C2、C2&C4 和失败率", "MECHANISM AND INSTABILITY");
addClaim(s, "C2 不能当严重程度曲线；failed fraction 是强非线性/非正常终止的辅助曲面。");
img(s, "C2_negative_damping_surface.png", 0.55, 1.55, 3.9, 3.1);
img(s, "C2C4_surface.png", 4.72, 1.55, 3.9, 3.1);
img(s, "failed_fraction_surface.png", 8.88, 1.55, 3.9, 3.1);
box(s, 0.65, 5.1, 3.75, 0.92, "C2", "机制层：总阻尼为负。低风速也可能触发，不能解释为严重程度单调增加。", "FFFFFF", C.blue);
box(s, 4.82, 5.1, 3.75, 0.92, "C2&C4", "严格同步：覆盖率低，但代表机制和增长同一时间步重合。", "FFFFFF", C.navy);
box(s, 8.98, 5.1, 3.75, 0.92, "Failed fraction", "不作为 galloping 判据，但强响应非正常终止必须报告。", "FFFFFF", C.red);
addFooter(s, n++);
addNotes(13, "C2、C2&C4 和失败率", "这一页回答可能的问题：为什么 C2 不随风速升高？因为大响应后气动状态不一定长期停在小扰动负阻尼区。失败率不是判据，但有物理意义，特别是强非线性响应导致 solver 难以完成。");

s = pptx.addSlide(); title(s, "下一步计划：从趋势曲面到临界边界", "NEXT STEPS");
addClaim(s, "当前结果支持趋势判断；下一阶段要扩展 L、校准 C7，并从 iso-coverage 提取边界。");
box(s, 0.78, 1.82, 3.55, 1.3, "1 扩展几何维度", "加入 L=250, 322.8, 450, 500 m；继续使用 H(L)=wL²/(8T0) 并做 sag sensitivity。", "FFFFFF", C.blue);
box(s, 4.55, 1.82, 3.55, 1.3, "2 校准工程限值", "C7 需要真实净空、相间距、tower geometry 或 utility threshold；之后再解释为工程风险。", "FFFFFF", C.amber);
box(s, 8.32, 1.82, 3.55, 1.3, "3 提取边界", "从 C6=50/80%、failed_fraction=20% 等 iso-coverage 生成 u_star_crit(L)。", "FFFFFF", C.green);
box(s, 0.78, 3.58, 3.55, 1.3, "4 配对天气 realization", "如果需要更严格比较，使用 paired seeds 或连续空间风场重采样。", "FFFFFF", C.cyan);
box(s, 4.55, 3.58, 3.55, 1.3, "5 增加物理机制", "加入 C5 频域 signature、C3 能量输入、C8 线性稳定边界。", "FFFFFF", C.navy);
box(s, 8.32, 3.58, 3.55, 1.3, "6 结构扩展", "束导线、覆冰形状、扭转耦合；Den Hartog 之外加入 Nigol/Clarke 类机制。", "FFFFFF", C.red);
addBullets(s, [
  "短期会议结论：当前 workflow 已能稳定产出多判据覆盖率曲面，但最终工程判定仍需要 C7 校准和更多 L levels。",
], 0.9, 5.95, 11.4, 0.45, { fontSize: 11 });
addFooter(s, n++);
addNotes(14, "下一步计划", "收尾时强调当前是趋势曲面阶段，不是最终工程规范结论。下一步最重要的是增加更多 L，校准 C7，并决定用哪个 iso-coverage 提取临界边界。");

s = pptx.addSlide(); title(s, "参考依据与可追溯文件", "REFERENCES AND TRACEABILITY");
addClaim(s, "所有判据和结果都可追溯到项目记录、原始文献提取和结果包。");
table(s, [
  [{ text: "类别", options: { bold: true, fill: C.pale } }, { text: "依据", options: { bold: true, fill: C.pale } }],
  ["机制/Den Hartog", "Week7 lecture; Den Hartog; Rossi et al. 2020; Chabart & Lilien 1998"],
  ["非线性响应/稳定性", "Zulli, Piccardo & Luongo; Ferretti et al.; Chabart & Lilien high-amplitude observations"],
  ["工程限值", "EN 50341 / National Grid RICA; IEC 60826; EN 50182; Timur baseline"],
  ["模型与工作流", "PROJECT_MEMORY.md; GALLOPING_CRITERIA.md; GEOMETRY_BASELINE.md"],
  ["最新结果", "output/time_step_coverage_audit/L300_350_400_ustar_grid_n4096_s3_plus_extra/result_package"],
], 0.8, 1.8, 11.75, 3.2, [2.6, 9.15], 8.4);
addBullets(s, [
  "会议中建议把 C7 明确说成“保留的工程后果通道”，不要把当前 C7 曲面作为已校准风险结论。",
  "建议把 common weather scenario 表述为“同一统计气象生成框架”，不是同一条完全相同风时程。"
], 0.95, 5.55, 11.4, 0.8, { fontSize: 10.5 });
addFooter(s, n++);
addNotes(15, "参考依据与可追溯文件", "最后用这一页回答出处问题。可以说：我们不是凭感觉设 limits，每个 limit 都对应文献或标准中的一类证据，同时所有数值结果都能回到项目结果包。");

const md = `# Galloping 会议汇报讲稿备注\n\n生成日期：2026-06-09\n\n${notes.join("\n")}`;
fs.writeFileSync(NOTES_PATH, md, "utf8");

pptx.writeFile({ fileName: PPTX_PATH });
console.log(PPTX_PATH);
console.log(NOTES_PATH);
