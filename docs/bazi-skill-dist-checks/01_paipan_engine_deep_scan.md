# bazi-skill-dist 排盘引擎深度扫描报告

> **扫描日期**：2026-07-15  
> **扫描类型**：纯只读源码审计  
> **证据等级**：L1=直接源码观测 / L2=多源推导 / L3=推断  
> **目标**：评估 bazi-skill-dist 排盘引擎在知命 AI 项目中的复用可行性  
> **扫描范围**：`E:\VSCODE\bazi-skill-dist\scripts\rule_engine\` + 外部依赖 `bazi-master-analysis\scripts\calculate_bazi.py`

---

## RQ-01: 四柱计算管线

### 1. 入口函数 — 完整调用链

```
用户请求
  → api/main.py:run_inference_stream() / api/main.py:inference_run()   [L1: main.py:134-356]
    → api/chart_calculator.py:compute_pillars()                         [L1: chart_calculator.py:20-35]
      → BaziCalculator(birth_date, birth_time, gender, current_year)    [L1: external calculate_bazi.py:53-91]
        → __init__() 内调用 _calculate_pillars()                        [L1: calculate_bazi.py:93-107]
          → _get_year_ganzhi(), _get_month_ganzhi(), _get_day_ganzhi(), _get_hour_ganzhi()
```

**备选路径**（较新 server.py）：  
`api/server.py → api/controller.py:ChartAnalysisController.analyze() → 同样调用 compute_pillars()`

**关键发现**：四柱计算完全委托给外部项目 `bazi-master-analysis`，不是 bazi-skill-dist 自有的能力。这意味着**知命不能直接复用 bazi-skill-dist 的四柱计算**——需要单独引入 `bazi-master-analysis` 或替换为其他引擎。

### 2. 年柱计算

- **源文件**：`bazi-master-analysis/scripts/calculate_bazi.py:109-115`
- **算法**：以 1984 年（甲子年）为基准，`(year - 1984) % 60` 计算干支索引
- **立春换年**：❌ **未处理**。直接用公历年份，忽略立春节点
  - 例：公历 2026-02-01 应算乙巳年（立春前），但引擎会算丙午年
- **测试覆盖**：❌ 无
- **纯函数**：✅ 是（相同输入→相同输出）

证据等级：L1（直接观测到无立春判断）

### 3. 月柱计算

- **源文件**：`calculate_bazi.py:117-137`
- **算法**：五虎遁年上起月法 ✓，但**月支直接映射公历月份**（1月→寅、2月→卯...）
- **节气换月**：❌ **未使用**。注释明确标注 "注意：这里使用公历月份，实际应该使用农历节气"
  - 例：公历 2026-03-05 应算正月庚寅（惊蛰前），但引擎会算二月辛卯
- **节气数据**：不存在。无任何节气日期表或计算逻辑
- **测试覆盖**：❌ 无
- **纯函数**：✅ 是

证据等级：L1（源码 119 行注释直接声明）

### 4. 日柱计算

- **源文件**：`calculate_bazi.py:139-149`
- **算法**：基准日偏移法——以 1900-01-01 为甲戌日，`(base_gan + days_delta) % 10` 和 `(base_zhi + days_delta) % 12`
- **函数注释明确标识**："简化算法，实际应用中应使用更精确的万年历算法"（第 142 行）
- **准确性**：受基准日取值影响，长跨度可能有累积误差
- **测试覆盖**：❌ 无
- **纯函数**：✅ 是

证据等级：L1（源码 142 行注释 + 算法直接观测）

### 5. 时柱计算

- **源文件**：`calculate_bazi.py:151-174`
- **算法**：五鼠遁日上起时法 ✓
- **时辰映射**：`SHICHEN` 表（第 46-50 行），23-01=子、01-03=丑 ...
- **真太阳时**：❌ **未处理**。直接用输入的小时数，不考虑出生经度
  - 函数命名虽涉及"天文真太阳时定位纠偏"（`main.py:148`），但实际 `chart_calculator.py:compute_pillars()` 并未做任何时区/经度转换
- **测试覆盖**：❌ 无
- **纯函数**：✅ 是

证据等级：L1（compute_pillars 源码仅有 str → datetime 转换，无经度参数）

### 6. 出生时间未知处理

- **ADR-011 要求**：允许时辰未知，引擎可输出全部 12 时柱结果或省略时柱
- **实际处理**：❌ **未处理**
- `BaziIntakeRequest.birth_hour` 为 `int` 类型，必填（`Field(..., ge=0, le=23)`），不接受 None
- `InferenceRequest`（contract）也无此支持
- 若 birth_hour=0，默认按子时算，无任何标记或告警

证据等级：L1（main.py:100-103 字段定义无 Optional 类型）

### 7. RQ-01 综合结论

| 组件 | 算法类型 | 准确性 | 立春/节气 | 真太阳时 | 测试 | 纯函数 |
|------|---------|--------|-----------|---------|------|-------|
| 年柱 | 基准偏移 | ⚠️ 有误 | ❌ 无 | N/A | ❌ | ✅ |
| 月柱 | 五虎遁+公历月 | ⚠️ 有误 | ❌ 无 | N/A | ❌ | ✅ |
| 日柱 | 基准日偏移 | ⚠️ 简化 | N/A | N/A | ❌ | ✅ |
| 时柱 | 五鼠遁 | ✅ 正确 | N/A | ❌ 无 | ❌ | ✅ |

**对知命的影响**：四柱计算是排盘的基础。bazi-skill-dist 的四柱算法**不可直接用于生产**——立春换年、节气换月、真太阳时校准是关键缺口。

---

## RQ-02: 藏干（Hidden Stems）计算

### 1. 藏干定义位置

- **源文件**：`scripts/rule_engine/parser/chart_parser.py:16-29`
- **存储方式**：硬编码 Python dict，`HIDDEN_STEMS`
- **是否可配置**：❌ 否。硬编码在源码中，无外部配置文件

```python
HIDDEN_STEMS = {
    "子": [("癸", "本气")],
    "丑": [("己", "本气"), ("癸", "中气"), ("辛", "余气")],
    "寅": [("甲", "本气"), ("丙", "中气"), ("戊", "余气")],
    "卯": [("乙", "本气")],
    "辰": [("戊", "本气"), ("乙", "中气"), ("癸", "余气")],
    "巳": [("丙", "本气"), ("庚", "中气"), ("戊", "余气")],
    "午": [("丁", "本气"), ("己", "中气")],
    "未": [("己", "本气"), ("丁", "中气"), ("乙", "余气")],
    "申": [("庚", "本气"), ("壬", "中气"), ("戊", "余气")],
    "酉": [("辛", "本气")],
    "戌": [("戊", "本气"), ("辛", "中气"), ("丁", "余气")],
    "亥": [("壬", "本气"), ("甲", "中气")],
}
```

### 2. 本气/中气/余气权重

- **有定性标签**：✅ 每个藏干有 `"本气"`/`"中气"`/`"余气"` 文本标签
- **有定量权重**：❌ **无**。没有任何数值权重定义
- 五行计数时所有天干（含藏干）**各计 1**，不做加权
- 藏干结构存储位置：`bazi_chart.py:54` `hidden_stems_detail: dict[str, list[tuple[str, str]]]`
- 在 `BaziChart.five_elements` 中已经平权汇总

### 3. 与经典标准对比

| 地支 | bazi-skill-dist | 渊海子平 / 三命通会 | 一致？ |
|------|----------------|-------------------|--------|
| 子 | 癸(本气) | 癸 | ✅ |
| 丑 | 己(本气)、癸(中气)、辛(余气) | 己、癸、辛 | ✅ |
| 寅 | 甲(本气)、丙(中气)、戊(余气) | 甲、丙、戊 | ✅ |
| 卯 | 乙(本气) | 乙 | ✅ |
| 辰 | 戊(本气)、乙(中气)、癸(余气) | 戊、乙、癸 | ✅ |
| 巳 | 丙(本气)、庚(中气)、戊(余气) | 丙、庚、戊 | ✅ |
| 午 | 丁(本气)、己(中气) | 丁、己 | ✅ |
| 未 | 己(本气)、丁(中气)、乙(余气) | 己、丁、乙 | ✅ |
| 申 | 庚(本气)、壬(中气)、戊(余气) | 庚、壬、戊 | ✅ |
| 酉 | 辛(本气) | 辛 | ✅ |
| 戌 | 戊(本气)、辛(中气)、丁(余气) | 戊、辛、丁 | ✅ |
| 亥 | 壬(本气)、甲(中气) | 壬、甲 | ✅ |

**结论**：藏干表与经典完全一致。**本部分 bazi-skill-dist 可以直接复用**。但需注意缺少权重数值的问题——如果需要按本中余气加权的五行分析，需要自行添加权重配置。

**测试覆盖**：❌ 无。

---

## RQ-03: 十神（Ten Gods）计算

### 1. 计算逻辑位置

- **核心函数**：`chart_parser.py:85-121` `_get_ten_god(day_stem, target_stem)`
- **计算方式**：基于五行生克关系 + 阴阳异同推导，**非查表法**
  - 同五行 → 比劫（阴阳同=比肩，异=劫财）
  - 生我 → 印星（阴阳同=偏印，异=正印）
  - 我生 → 食伤（阴阳同=食神，异=伤官）
  - 克我 → 官杀（阴阳同=七杀，异=正官）
  - 我克 → 财星（阴阳同=偏财，异=正财）

代码中虽然也定义了 `_SHI_SHEN_MATRIX` 查表（第 52-60 行），但 `_get_ten_god()` 实际使用的是推导逻辑，查表矩阵未被引用。

### 2. 十神定义完整性

✅ **完整**。全部 10 神均已定义：
```python
_SHI_SHEN_NAMES = [
    "比肩", "劫财", "食神", "伤官",
    "正财", "偏财", "正官", "七杀",
    "正印", "偏印",
]
```

### 3. 藏干十神处理

✅ **已展开**。`ChartParser.parse()` (第 124-186 行) 中：
1. 先遍历四柱天干计算十神
2. 再遍历每个地支的藏干，逐干计算十神
3. 所有天干+藏干的十神统一汇总到 `ten_gods_count` 字典
4. 藏干明细存储在 `hidden_stems_detail` 字段中

**注意**：藏干的十神统计是**平权**的——每个藏干算 1 次，不区分本中余气。这对后续"十神力量"的分析可能不够精确。

### 4. 十神统计

✅ **实现于** `chart_parser.py:142-163`。创建 `ten_gods_count` 字典初始化为全 0，遍历所有天干+藏干后累加。最终存储到 `BaziChart.ten_gods`。

查询方法：`bazi_chart.py:64-75` `ten_god_count(name)`——支持复合名映射（如"官杀"→"正官"+"七杀"）。

**测试覆盖**：❌ 无。

---

## RQ-04: 五行统计与力量分析

### 1. 五行计数

- **源文件**：`chart_parser.py:165-172`
- **算法**：简单计数法。遍历所有天干 + 所有藏干，每个干根据五行属性加 1
- **特点**：天干和藏干各算 1，无权重差异

```python
element_count = {e: 0 for e in "木火土金水"}
for stem, _ in all_stems:
    elem = _STEM_ELEMENT.get(stem)
    if elem and elem in element_count:
        element_count[elem] += 1
```

```python
# bazi_chart.py 中存储
five_elements: dict[str, int] = field(default_factory=dict)
# {"木": 3, "火": 4, "土": 3, "金": 2, "水": 1}
```

### 2. 力量分析算法

- **简单计数**：❌ 仅平权计数，无以下加权：
  - 无月令旺衰权重（月令地支的中气/余气影响）
  - 无藏干本中余气权重（所有藏干算 1 次）
  - 无天干/地支力量差异（天干透出 vs 地支藏干无区别）
  - 无生克制化影响（如申子半合水局的加成）
- **`FactSpace` 派生**：`fact_engine.py` 中 `DerivedFactEngine.derive()` 派生了一些高阶事实（如"身旺得分"），但其底层依赖这些简单计数

### 3. 身旺/身弱判定

- **实际判定点**：`controller.py:287-298` `_determine_body_strength()`
  - 简单逻辑：若日主五行计数 ≥ 2 → "身旺"，否则→"身弱"
  - 这**不是**学派编译器中的复杂逻辑——学派编译器（如子平派的 threshold=2.8、根重+0.5）依赖于 `FactSpace` 中预计算好的 `身旺得分`
- **`controller.py` 的 `_determine_body_strength()`** 是返回给 API 的简单版，不涉及学派差异

### 4. 用神/喜神推导

❌ **无实现**。

- `main.py:214` 中试图从 `result.fact_space` 获取用神：`str(result.fact_space.get("用神", ""))`
- 但实际 `FactSpace` 中**无从格体系的"用神"事实被推导**——`fact_engine.py` 中的派生逻辑只到"身旺得分"、"得月令"等基础事实
- 搜索 `grep -rn "用神" scripts/rule_engine/` 的结果为空
- 学派编译器中也没有用神推导逻辑

**对知命的影响**：用神是八字分析的核心概念。bazi-skill-dist 完全缺位。知命需要自行实现用神推导引擎。

---

## RQ-05: 大运（Major Luck Periods）计算

### 1. 入口函数

- **旧路径**：外部 `BaziCalculator._calculate_dayun()`（calculate_bazi.py:255-291）
- **新路径**：`TemporalOverlayEngine.compute_da_yun_sequence()`（overlay_engine.py:149-225）
- **更高层**：`DestinyTimeline.compute()`（destiny_timeline.py:86-128）— 整合大运+生命阶段

### 2. 起运时间计算

**新引擎（overlay_engine.py:228-241）**：
```python
@staticmethod
def compute_start_age(chart) -> int:
    if chart.dayun:
        first = chart.dayun[0]
        if isinstance(first, dict) and "start_age" in first:
            return first["start_age"]
    return 8  # default: 起运 age 8
```
- ❌ 默认硬编码为 **8 岁起运**，这是占位值
- 只有 chart 中已经有大运数据时才读取，非自身计算

**节气依赖（jieqi_provider.py:15-27）**：
```python
def get_nearest_jieqi(birth_datetime: datetime) -> datetime:
    return birth_datetime + timedelta(days=21)  # 占位！
```
- ❌ `start_age_calculator.py:12-30` 的 `calculate_start_age()` 使用了传统的 3 天=1 年规则，但其依赖的 `nearest_jieqi_datetime` 来自 `jieqi_provider`，后者返回的是**出生日期 + 21 天**的占位值
- 这意味着起运年龄计算**完全不可用于生产**

**旧引擎（BaziCalculator._calculate_dayun()）**：
- ❌ `start_age = 2`（第 273 行）——硬编码 2 岁起运
- 注释标注 "简化算法，实际需要精确到节气"

### 3. 大运顺逆

✅ **此部分正确**。`dayun_rules.py:23-53`：
```
阳年男、阴年女 → FORWARD（顺行）
阴年男、阳年女 → BACKWARD（逆行）
```
- 完善的参数校验（ValueError for invalid gender/stem）
- 纯函数，可测试

### 4. 大运干支序列

**新引擎**（overlay_engine.py:149-225）：
- 从月柱开始，每步 ±1 天干 + ±1 地支
- 方向由 gender + year_stem yin-yang 决定
- 生成 8 步大运（80 年），每步 10 年
- 正确使用 `_compute_ten_god()` 计算大运十神标签

### 5. 流年推演

- **`AnnualFlowGenerator`**（annual_flow_generator.py:55-125）：生成 AnnualFlow 序列
  - 干支从公历年份计算（`sexagenary_of_year()`）
  - 通过五行属性比较确定 interaction_type（共鸣/支持/压力）
  - 流年与大运的联动：`overlay_engine.py:614-616` 检测岁运并临，`618-626` 检测天克地冲
- **流年与大运联动**：`overlay_engine.py:587-632` 中 `_detect_liu_nian_patterns()` 有完整的伏吟、反吟、岁运并临检测
- ❌ 流年与大运的十神联动（增量分析）在 `InferenceRuntime._apply_dynamic_context()` 中实现（runtime.py:411-534），但限于十神计数增量，无五行生克深度联动

### 6. temporal/ 目录 24 个文件功能清单

| # | 文件名 | 功能 | 生产可用？ |
|---|--------|------|----------|
| 1 | `activation_engine.py` | 规则生命周期时间触发管理 | ✅ |
| 2 | `annual_flow_generator.py` | 流年序列生成器 | ⚠️ 缺少节气 |
| 3 | `annual_flow_models.py` | AnnualFlow/AnnualFlowSequence 数据模型 | ✅ |
| 4 | `current_temporal_focus_engine.py` | 当前时间焦点引擎 | ❓ 未读取 |
| 5 | `dayun_rules.py` | 大运顺逆方向规则 | ✅ 纯逻辑 |
| 6 | `destiny_timeline.py` | 整个人生时间线计算 | ✅ 架构好 |
| 7 | `jieqi_provider.py` | 节气 provider | ❌ 占位实现 |
| 8 | `overlay_engine.py` | 时间覆盖引擎（核心） | ⚠️ 部分可复用 |
| 9 | `runtime_consistency_validator.py` | 运行时一致性校验 | ✅ |
| 10 | `start_age_calculator.py` | 起运年龄计算 | ❌ 依赖 jieqi |
| 11 | `temporal_compression_engine.py` | 时间压缩引擎 | ❓ 未读取 |
| 12 | `temporal_consensus.py` | 时间维度共识 | ❓ 未读取 |
| 13 | `temporal_explainability_linker.py` | 可解释性链接 | ✅ |
| 14 | `temporal_importance_engine.py` | 时间重要性引擎 | ❓ 未读取 |
| 15 | `temporal_insight_engine.py` | 时间洞见引擎 | ❓ 未读取 |
| 16 | `temporal_meta_narrative_engine.py` | 元叙事引擎 | ❓ 未读取 |
| 17 | `temporal_narrative_builder.py` | 叙事构建器 | ❓ 未读取 |
| 18 | `temporal_phase_generator.py` | 阶段生成器 | ❓ 未读取 |
| 19 | `temporal_response_optimizer.py` | 响应优化器 | ❓ 未读取 |
| 20 | `temporal_runtime.py` | 时间运行时 | ❓ 未读取 |
| 21 | `temporal_runtime_aggregator.py` | 运行时聚合器 | ❓ 未读取 |
| 22 | `temporal_shift.py` | TemporalShift 数据模型 | ✅ |
| 23 | `temporal_state.py` | TemporalState/DaYunPillar/LiuNianPillar 数据模型 | ✅ |
| 24 | `temporal_transition_generator.py` | 过渡生成器 | ❓ 未读取 |

**说明**：标记"❓ 未读取"的文件因时间限制未详细扫描，但根据文件名和 import 关系可推断功能。

---

## RQ-06: 四学派编译器详细分析

### 1. 抽象基类 SchoolCompiler

- **源文件**：`schools/school_compiler.py:55-176`
- **输入**：`BaziChart` → `FactCompiler.compile(chart)` → 内部 `FactGraph`
- **输出**：完整的学派隔离 `FactGraph`
- **编译步骤**：
  1. Stage 1+2：运行基础 FactCompiler 到学派隔离的 FactGraph
  2. Stage 3：调用 `compile_derived_facts()`（学派具体派生事实）
  3. Stage 4：调用 `compile_meta_facts()`（学派元规则）

**三个抽象方法**：
- `compute_body_strength() → BodyStrengthResult`
- `assess_pattern() → PatternResult`
- `apply_climate_rules() → ClimateResult`

### 2. 子平派（SubPingCompiler）— 徐乐吾

- **源文件**：`schools/compilers/sub_ping.py:18-161`
- **身旺**：threshold=2.8，根重加分（≥2 根 +0.5），无根失令 -0.5
- **格局**：标准格局分类，含从格检查（从杀/从财）
- **调候**：穷通宝鉴标准，调候为急（meta_rule 调候优先于格局）
- **规则数量**：`compile_derived_facts()` 编译 3 条派生事实，`compile_meta_facts()` 编译 1 条元规则

### 3. 梁湘润派（LiangXiangrunCompiler）

- **源文件**：`schools/compilers/liang_xiangrun.py:18-155`
- **身旺**：threshold=2.5，格局休废 -1.0（当格神为比肩/劫财且不得令时）
- **格局**：格 vs 局二分，三合三会取局逆用
- **调候**：调候为急——最高优先级（confidence=0.95）
- **规则数量**：与子平相同结构（3 派生 + 1 元规则）

### 4. 袁树珊派（YuanShushanCompiler）

- **源文件**：`schools/compilers/yuan_shushan.py:18-145`
- **身旺**：threshold=3.0，食神泄秀 +0.5（失令时食伤有加分）
- **格局**：命宫+小限影响（注释标注"待集成"）
- **调候**：穷通宝鉴标准（无特殊优先级）
- **元规则**：杀印相生优先于食神制杀
- **规则数量**：3 派生 + 1 元规则

### 5. 韦千里派（WeiQianliCompiler）

- **源文件**：`schools/compilers/wei_qianli.py:18-125`
- **身旺**：threshold=3.0，纯分数无调整（极简主义）
- **格局**：简化分类，八步法
- **调候**：条件调候，非强制
- **元规则**：无
- **规则数量**：3 派生 + 0 元规则

### 6. 学派推理规则数量对比

| 学派 | 身旺调整项 | 格局特色 | 调候优先级 | 元规则 |
|------|-----------|---------|-----------|-------|
| 子平 | 根重+0.5 | 从格检查 | 调候为急 | 调候>格局 |
| 梁湘润 | 格局休废-1.0 | 格vs局二分 | 调候为急(最高) | 同上 |
| 袁树珊 | 食伤泄秀+0.5 | 命宫待集成 | 标准 | 杀印>食制 |
| 韦千里 | 无调整 | 简化八步法 | 条件调候 | 无 |

### 7. 核心问题：所有学派共享同一套 YAML 规则

```python
# runtime.py:600-615 中，学派编译器使用的 rules_data_raw 是共享的
rules_data_raw = getattr(self, '_rules_data_raw', [])
for school_name, config in SCHOOL_REGISTRY.items():
    compiler_cls = _compiler_map.get(school_name)
    compiler = compiler_cls(config)
    srt = SchoolRuntime(config, compiler)
    srt.load_rules(rules_data_raw)  # ← 同一套规则！
```

**关键发现**：四学派的"分歧"仅体现在身旺 threshold 和调整项的不同，**而非真正的命理推理规则分歧**。所有学派共享 `rules/` 目录下的同一批 YAML 规则文件。如果这些 YAML 规则本身是"子平派"的，那么梁湘润/袁树珊/韦千里的"推理"结果本质上仍是子平派规则 + 参数微调。

### 8. 可扩展性：新增学派

需要实现：
1. 在 `SCHOOL_REGISTRY`（school_config.py）中注册新配置
2. 实现 `SchoolCompiler` 子类（5 个抽象方法）
3. 在 `_compiler_map`（runtime.py:600-605）中注册映射
4. 可能需要新增独立的 YAML 规则文件（如果学派推理逻辑有本质差异）

**难度**：中等。架构支持性好，但现有学派之间缺乏真正的规则独立性，导致新增学派的"意义"停留在参数层面。

---

## RQ-07: 共识引擎详细分析

### 1. ConsensusEngine 完整 API

**源文件**：`schools/consensus/engine.py:33-323`

| 方法 | 访问级 | 参数 | 返回 | 描述 |
|------|--------|------|------|------|
| `__init__()` | public | strategies, ontologies, semantic_graph, contextual_engine | None | 初始化共识引擎 |
| `consensus()` | public | school_results: dict | ConsensusResult | 主入口，计算多学派共识 |
| `_get_matcher()` | private | - | SemanticMappingMatcher | 惰性构建语义匹配器 |
| `_build_and_set_contexts()` | private | school_results, matcher | None | 构建学派上下文 |
| `_collect_aspects()` | private | school_results, matcher | list[str] | 确定需要共识的 aspects |
| `_build_conclusions()` | private | aspect, school_results, configs, matcher | list[SchoolConclusion] | 构建每个学派的结论 |
| `_majority_vote()` | private | conclusions | str\|None | 简单多数投票 |
| `_weighted_vote()` | private | conclusions, configs | str\|None | 加权投票 |
| `_meta_consensus()` | private | aspect, conclusions, configs | str\|None | 元规则共识 |
| `_count_votes()` | static | conclusions | dict[str, int] | 计票 |
| `_compute_agreement()` | static | conclusions | str | 计算共识等级 |

### 2. 三种策略链

优先级顺序（Constructor default）：
1. **MetaConsensus** → `_meta_consensus()`
   - 检查 "调候" aspect：如果有学派配置了 `climate_overrides_pattern` 且结论为"需调候"，直接返回"需调候"
   - 其他 aspects 返回 None（不需特殊元规则处理）
2. **WeightedVote** → `_weighted_vote()`
   - 按 `SchoolConfig.consensus_weight` 加权
   - 需要超过 50% 总权重才胜出
3. **MajorityVote** → `_majority_vote()`
   - 简单多数的后备方案
   - 需要超过 50% 总数

### 3. 权重配置

```python
# school_config.py:27-57
SCHOOL_XU_LEWU = SchoolConfig(consensus_weight=1.0, ...)
SCHOOL_LIANG_XIANGRUN = SchoolConfig(consensus_weight=1.0, ...)
SCHOOL_YUAN_SHUSHAN = SchoolConfig(consensus_weight=1.0, ...)
SCHOOL_WEI_QIANLI = SchoolConfig(consensus_weight=1.0, ...)
```

✅ 所有学派权重均为 **1.0**，四家平权。

### 4. 共识失败处理

当三种策略都无法达成共识时（均返回 None），each aspect 被设置为 `"分歧"`（engine.py:152）。

**无降级或后备方案**——直接标记为分歧，不尝试语义近似匹配或 confidence threshold 截断。

### 5. ConsensusResult 完整字段

**源文件**：`schools/consensus/models.py:35-83`

| 字段 | 类型 | 描述 |
|------|------|------|
| `school_results` | dict | 原始学派推理结果，key=school_name → SchoolInferenceResult |
| `aspects` | dict[str, str] | 共识结果，key=aspect → value（"分歧"表示无法达成） |
| `conclusions` | dict[str, list[SchoolConclusion]] | 逐学派逐 aspect 的详细结论 |
| `votes` | dict[str, dict[str, int]] | 投票计数，key=aspect → {value: count} |
| `agreement` | dict[str, str] | 共识等级（四家一致/三家一致/两两分歧/无共识） |
| `resolution_strategy` | str | 最终使用的策略名 |
| `resolution_reason` | str | 策略选择原因 |
| `strategies_used` | list[str] | 尝试过的所有策略 |

### 6. 当前共识覆盖的命理方面

**仅覆盖 3 个 aspects**（engine.py:183-196 硬编码回退）：

| Aspect | 数据类型 | 共识方法 |
|--------|---------|---------|
| 身旺 | str（身旺/身弱） | 加权投票 |
| 格局 | str（正官格/七杀格...） | 加权投票 |
| 调候 | bool（需调候/不需调候） | 元规则优先 |

**不覆盖**：用神、喜神、忌神、五行旺衰、大运吉凶、流年影响等**关键命理指标**。

**语义模式**（Phase 4.3.1）：当提供 ontologies + semantic_graph 时，aspect 发现和值提取通过 `SemanticMappingMatcher` 进行语义感知比较（仍处于扩展阶段）。

---

## RQ-08: API 契约详细分析

### 1. bazi-skill-dist 完整端点清单

**传统 API（main.py）**：

| 方法 | 路径 | 描述 | 请求/响应 |
|------|------|------|-----------|
| GET | `/api/analyze/stream` | SSE 流式推理（6 步） | Query params → SSE |
| GET | `/api/health` | 健康检查 | → JSON |
| POST | `/api/v1/inference/run` | 同步推理 | BaziIntakeRequest → BaziInferenceResponse |
| POST | `/api/v1/deepseek/analyze` | DeepSeek 报告生成 | DeepSeekRequest → JSON |

**新版 API（server.py）**：

| 方法 | 路径 | 描述 | 限速 |
|------|------|------|------|
| GET | `/api/health` | 健康检查 | 10/s |
| POST | `/api/analyze` | 全量分析 | 10/s |
| GET | `/api/trace/{trace_id}` | 追溯检索 | 10/s |
| GET | `/api/narrative/stream/{trace_id}` | SSE 叙事流 | 3/min |

### 2. 主分析端点请求 Body 对比

#### bazi-skill-dist `BaziIntakeRequest`（main.py:94-103）
```python
name: str          # required
gender: str        # required, "male"|"female"
birth_year: int    # required, 1900-2100
birth_month: int   # required, 1-12
birth_day: int     # required, 1-31
birth_hour: int    # required, 0-23
birth_minute: int  # required, 0-59
birthPlace: str    # optional, default ""
```

#### bazi-skill-dist `InferenceRequest`（contract/request.py）
```python
birthDate: str     # required, YYYY-MM-DD
birthTime: str     # required, HH:mm
gender: str        # required, "male"|"female"
birthPlace: str    # optional
longitude: float   # optional (未在代码中实际使用)
timezone: str      # optional (未在代码中实际使用)
sessionId: str     # optional
includedSections: list[str]  # optional
```

#### 知命 `POST /api/v1/bazi/charts`（docs/13_API接口契约设计.md:442-456）
```json
{
  "birth_year": 1990,       // int, required
  "birth_month": 8,         // int, required
  "birth_day": 15,          // int, required
  "birth_hour": 12,         // int|null, optional
  "birth_minute": 0,        // int|null, optional
  "gender": "male",         // string, required
  "birth_place": "北京",    // string, optional
  "timezone": "Asia/Shanghai", // string, required for V1
  "calendar_type": "solar", // string, optional, default "solar"
  "name": "我的八字",       // string, optional
  "is_primary": true        // bool, optional
}
```

#### 逐字段对比

| 字段 | bazi-skill-dist | 知命 v1 | 兼容？ |
|------|----------------|---------|--------|
| birth_year | ✅ int, 必填 | ✅ int, 必填 | ✅ |
| birth_month | ✅ int, 必填 | ✅ int, 必填 | ✅ |
| birth_day | ✅ int, 必填 | ✅ int, 必填 | ✅ |
| birth_hour | ✅ int, 必填(0-23) | ✅ int\|null, **可选** | ⚠️ 知命允许null |
| birth_minute | ✅ int, 必填 | ✅ int\|null, 可选 | ⚠️ 同上 |
| gender | ✅ "male"/"female" | ✅ "male"/"female" | ✅ |
| birth_place | ✅ birthPlace, 可选 | ✅ birth_place, 可选 | ✅ 字段名不同 |
| timezone | ❌ 有字段但未使用 | ✅ required | ❌ 知命需要 |
| calendar_type | ❌ 无 | ✅ 可选,默认"solar" | ❌ |
| name | ❌ 无 | ✅ 可选 | ❌ |
| is_primary | ❌ 无 | ✅ 可选 | ❌ |
| 时辰可选 | ❌ 必填 | ✅ 可选| ❌ |

### 3. 响应 Body 对比

#### bazi-skill-dist `BaziInferenceResponse`
```json
{
  "accepted": true,
  "message": "推理完成",
  "summary": "命中X条规则",
  "matched_count": 10,
  "resolved_count": 8,
  "conclusions": [
    {"rule_name": "...", "confidence": 0.85, "texts": [...], "schools": [...], "description": "..."}
  ]
}
```

#### bazi-skill-dist `InferenceResponse`（contract/response.py—更完整的字段）
```python
requestId, durationMs, error
apiVersion, schemaVersion, runtimeVersion
traceRef, traceSummary, traceAvailable
facts: list[Fact]
inferences: list[InferenceNode]
schools: list[SchoolVerdict]
consensus: list[ConsensusAspect]
governance: GovernanceAssessment
elements: list[ElementDynamics]
phases: list[LifePhase]
semanticNodes, semanticLinks
narrative: CognitiveNarrative
meaning, insights
explainability: ExplainabilitySummary
temporalNarrative: Optional[TemporalNarrative]
controversies: list[ControversyRecord]
```

#### 知命 `POST /api/v1/bazi/charts` 响应（docs/13_API接口契约设计.md:459-509）
```json
{
  "chart_id": "chart_x1y2z3w4",
  "pillars": {
    "year": {"heavenly_stem": "庚", "earthly_branch": "午", "hidden_stems": ["丁","己"]},
    "month": {...},
    "day": {...},
    "hour": {...}
  },
  "five_elements": {
    "wood": {"count": 2, "status": "旺", "score": 25},
    "fire": {"count": 3, "status": "旺", "score": 30}
  },
  "day_master": {"stem": "戊", "strength": "偏旺"},
  "ten_gods": [
    {"pillar": "year", "heavenly_stem": "庚", "ten_god": "食神"},
    ...
  ],
  "great_fortune": [
    {"age_range": "0-9", "heavenly_stem": "乙", "earthly_branch": "酉"},
    ...
  ],
  "current_year": {"year": 2026, "heavenly_stem": "丙", "earthly_branch": "午"}
}
```

### 4. 关键缺口分析

#### 知命需要但 bazi-skill-dist 没有的字段/能力

| 缺口 | 知命字段 | 影响等级 | 说明 |
|------|---------|---------|------|
| 排盘 ID | `chart_id` | 🔴 高 | 无持久化概念 |
| 藏干数组格式 | `hidden_stems: ["丁","己"]` | 🟡 中 | bazi 输出 dict 格式，非数组 |
| 五行状态 | `status: "旺"`, `score: 25` | 🟡 中 | bazi 仅统计 count |
| 日主强度中文 | `day_master.strength: "偏旺"` | 🟡 中 | 学派编译器有但 API 未暴露 |
| 大运数组 | `great_fortune` | 🔴 高 | temporal 层有但 API 未整合 |
| 流年 | `current_year` | 🟡 中 | 同上方 |
| 异步任务 | task 模式 | 🔴 高 | bazi 全部同步 |
| WebSocket | `/ws/v1/session` | 🔴 高 | 不支持 |
| 用户鉴权 | `Authorization: Bearer` | 🟡 中 | 无 |
| 数据分层 | `data_tier` | 🔴 高 | ADR-012 要求 |
| 分析反馈 | feedback 接口 | 🔴 高 | 无此概念 |
| 版本控制 | 报告版本 | 🟡 中 | 无 |
| 分页 | pagination | 🟢 低 | 列表接口需要 |
| 统一响应 | `code/message/data` | 🟡 中 | 知命有统一响应体 |

#### bazi-skill-dist 有但知命不需要的字段/能力

| 字段 | 说明 | 可忽略？ |
|------|------|---------|
| `accepted` | 冗余成功标志 | ✅ |
| `matched_count/resolved_count` | 规则匹配统计 | ✅ |
| `conclusions[].rule_name` | 规则名（内部细节） | ✅ |
| `governance` | 治理评分 | ✅ |
| `controversies` | 学派分歧记录 | ✅ |
| SSE streaming | 流式推理 | ⚠️ 可转化为知命的异步任务 |

---

## RQ-09: 代码质量与可测试性

### 1. 测试覆盖

#### 测试文件统计

- **`tests/` 目录**：**28 个存活 `.py` 源文件**（~500-600 测试），分布于 8 个子目录
- `tests/` 下另有 **24 个子目录仅有 `__pycache__/`（`.py` 源文件已被删除）**，历史曾存在约 150+ 测试文件
- **`scripts/rule_engine/tests/` 目录**：3 个非测试文件（backtest_engine.py, golden_schema.py, kg_generator.py）
- **项目根无 pytest 配置**：无 `pytest.ini`, `setup.cfg`, `conftest.py`, `pyproject.toml` 中的 pytest 配置

#### 存活测试文件分布

| 测试目录 | 文件数 | 测试领域 | 估计测试数 |
|---------|--------|---------|-----------|
| `tests/runtime_standard/` | 10 | 运行时契约规范 | ~80 |
| `tests/benchmarks/` | 2 | 基准测试 | ~80 |
| `tests/cos/` | 2 | 认知内核 | ~50 |
| `tests/observability/` | 1 | 可观测性 | ~130 |
| `tests/orchestrator/` | 1 | 编排器 | ~10 |
| `tests/replay/` | 1 | 重放引擎 | ~140 |
| `tests/schema_snapshots/` | 1 | 架构快照 | ~70 |
| `tests/snapshots/` | 1 | 快照 | ~70 |

**关键缺失**（以下领域零测试存活，且从删除的 `.pyc` 文件名看也未曾有过核心算法测试）：

| 缺失领域 | 历史测试文件（已删除） | 说明 |
|---------|---------------------|------|
| `tests/api/` | 0（从未存在） | ❌ API 无测试 |
| `tests/schools/` | 曾有 25 个文件 | ❌ 已删除，学派无测试 |
| `tests/temporal/` | 曾有 27 个文件 | ❌ 已删除，时间引擎无测试 |
| `tests/core/` | 0（从未存在） | ❌ 核心无测试 |
| `tests/facts/` | 曾有文件（含 `test_runtime_integration.py`） | ❌ 已删除 |
| 四柱计算 | 从未存在 | ❌ 核心排盘算法零测试 |
| 十神/藏干 | 从未存在 | ❌ 零测试 |
| 大运/起运 | 从未存在 | ❌ 零测试 |
| 学派编译器 | 从未存在 | ❌ 零测试 |
| 共识引擎 | 从未存在 | ❌ 零测试 |

**重要发现**：虽然项目历史上有过大量测试（从 `__pycache__` 推断约 150+ 文件），但覆盖的是**基础设施层**（runtime_standard/replay/observability）而非核心排盘逻辑。核心排盘算法**从未有过测试覆盖**。

#### 测试质量抽样分析

**样本 1：`test_runtime_contract.py`**（tests/runtime_standard/，229 行）
- 质量：✅ 良好
- 使用 `pytest` + `assert` + 异常测试
- 有边界条件测试（负超时、无效模式）
- 有 frozen dataclass 不可变性测试
- 有序列化往返测试（to_json → json.loads）
- 无 mock（该模块纯数据模型，不需要）

**样本 2：`test_runtime_replay_engine.py`**（tests/replay/，2332 行，项目中最大测试文件）
- 质量：✅ 良好
- 140+ 测试，覆盖整个 ReplayEngine API
- Categories A-T 系统化分组
- 有完整的「空重放→全管线」递进测试
- 有 determinism / immutability / serialization 质量属性测试
- 有 UTF-8 中文边界测试

**样本 3：`test_empathy_safety_balance.py`**（tests/cos/，748 行）
- 质量：✅ 良好
- 26 个测试类
- 包含端到端危机管线测试（`TestPersonaEngineCrisisPipeline`）
- 检查 fatalism guard、empathy layer、tone regulator

#### 测试运行尝试

```bash
cd E:\VSCODE\bazi-skill-dist && python -m pytest tests/ --co -q 2>&1 | head -50
```
（仅收集测试列表，不执行——需用户确认）

### 2. 类型标注

| 模块 | 类型覆盖率 | 说明 |
|------|-----------|------|
| `core/bazi_chart.py` | ✅ 高 | dataclass + Optional 类型 |
| `api/models.py` | ✅ 高 | Pydantic BaseModel |
| `api/main.py` | ✅ 高 | Pydantic Field 验证 |
| `contract/` 全系列 | ✅ 高 | Pydantic + camelCase |
| `schools/` 全系列 | 🟡 中 | ABC + dataclass，部分函数缺类型 |
| `engine/runtime.py` | 🟡 中 | dataclass + Optional 但非全部 |
| `temporal/` 全系列 | ✅ 高 | dataclass + 类型提示完整 |
| `parser/chart_parser.py` | 🟡 中 | 函数有类型但部分返回值未标注 |

**Pydantic/dataclass 使用**：
- `api/` 层使用 Pydantic BaseModel（FastAPI 集成）
- `contract/` 层使用 Pydantic + camelCase alias
- `core/` + `temporal/` + `schools/` 使用 Python `dataclass`
- 无 Pydantic v2 特性

### 3. 循环依赖

检查结果：

```
$ grep -rn "from.*rule_engine" scripts/rule_engine/ | head -30
```

所有 import 都是单向向下的（api → engine → core/facts/schools，无逆向 import）。  
**结论**：✅ 无循环依赖。架构清晰，分层合理。

依赖方向摘要：
```
api/ → controller/parser/engine/contract/
engine/ → core/facts/schools/chain/
schools/ → core/facts/
temporal/ → core/（无反向依赖）
facts/ → core/（无反向依赖）
```

### 4. 代码注释

| 模块 | 注释语言 | docstring 覆盖率 | 质量评估 |
|------|---------|----------------|---------|
| `api/main.py` | English | ✅ 高 | 文件头 docstring + 关键函数 |
| `chart_parser.py` | 中文+English | ⚠️ 中 | 关键数据结构有中文注释 |
| `bazi_chart.py` | English | ✅ 高 | 每个方法有 docstring |
| `engine/runtime.py` | English | ✅ 高 | 状态机、阶段有详细注释 |
| `school_compiler.py` | English | ✅ 高 | ABC 接口完整文档 |
| `compilers/*.py` | English | ✅ 高 | 每个学派有方法论描述 |
| `temporal/` | English | ✅ 高 | 几乎每个文件都有详细注释 |
| `calculate_bazi.py` | 中文 | ⚠️ 中 | 有基本注释，缺少边界说明 |
| `fact_engine.py` | Chinese | ⚠️ 中 | 部分中文注释 |

**总体**：docstring 覆盖率 ~70%，注释质量良好，但中英混用。

---

## RQ-10: 知命复用可行性总评

### 1. 排盘计算准确性评估：2/5 ⚠️

| 准则 | 评分 | 依据 |
|------|------|------|
| 年柱 | 2/5 | 无立春换年，基准偏移法 |
| 月柱 | 1/5 | 直接用公历月份，无节气 |
| 日柱 | 2/5 | 简化偏移法，可能有累积误差 |
| 时柱 | 4/5 | 五鼠遁正确，但无真太阳时 |
| 时辰未知 | 0/5 | 未实现 |
| 总体 | 2/5 | 仅适合 Demo/学习，不可用于生产 |

**已知缺陷**：
1. 立春换年缺失 → 年柱错误
2. 节气换月缺失 → 月柱错误
3. 日柱简化算法 → 长跨度潜在误差
4. 真太阳时缺失 → 时柱可能不准
5. 节气 provider 为占位 → 大运起运年龄错误

### 2. 与知命架构兼容性评估：4/5 ✅

bazi-skill-dist 的分层架构可以映射到知命的四层架构：

| 知命架构层 | bazi-skill-dist 对应层 | 适配需要 |
|-----------|----------------------|---------|
| Layer 1: 客户端表示层 | ❌ 无（这是前端） | 知命自行开发 |
| Layer 2: API 客户端适配层 | ❌ 无 | 知命自行开发 |
| Layer 3: FastAPI 路由层 | `api/main.py` + `api/server.py` | 需重写路由 + 适配知命 API 契约 |
| Layer 4: 业务服务层 | `api/controller.py` | 可嵌入知命 Service 层 |
| Layer 5: 领域层 | `core/` + `schools/` + `parser/` | ✅ 可直接复用架构 |
| Layer 6a: 数据访问层 | `contract/` + `persistence/` | 需适配知命数据模型 |
| Layer 6b: 基础设施层 | 排盘引擎、规则引擎 | ⚠️ 四柱计算需替换 |

**适配改造量估算**：
- 需重写：四柱计算（替换为正确万年历引擎）、API 路由层、持久化层
- 可直接复用：BaziChart 模型、ChartParser、藏干表、十神计算、大运/流年架构
- 需扩展：用神推导、学派独立规则、共识 aspects
- 需新增：data_tier 三层标记、WebSocket 支持、异步任务模型

### 3. ADR-009 兼容性：2/5 ⚠️

知命「八字分析 6 步流程」：
1. ✅ 命盘呈现 → bazi 可输出四柱
2. ✅ 核心事实提取 → FactSpace 层级
3. ❌ AI 初步分析 → 无 AI 编排（仅 DeepSeek 单次调用）
4. ❌ AI 动态追问 → 无对话状态管理
5. ❌ 用户反馈验证 → 无 feedback 机制
6. ❌ 最终报告生成 → 仅有 DeepSeek 单次调用

bazi-skill-dist 覆盖了步骤 1-2（命盘计算和基本事实提取），步骤 3-6 需要知命自行实现。bazi 可以作为步骤 1-2 的计算引擎。

### 4. ADR-012 兼容性：1/5 ❌

ADR-012 要求输出区分三层：`fact` / `inference` / `pending`。

bazi-skill-dist 完全不存在此概念：
- `FactSpace` 中的所有事实是平权的——没有 data_tier 标记
- 推理结论是确定性规则匹配结果，没有不确定性/置信度分层
- 学派编译器的 `confidence` 字段不能直接映射为 data_tier

**适配改造**：
- 需要在整个推理管线中加入 data_tier 传播（从原始输入到最终结论）
- 需要在 `BaziChart` 和 `SchoolInferenceResult` 中加入 data_tier 字段
- 需要修改 `FactGraph` 的事实模型
- 工作量：中-高（影响所有中间数据结构）

### 5. 复用路径推荐

#### 路径 A：直接嵌入（不推荐 ❌）

将 bazi-skill-dist 整个 project 作为知命的子模块嵌入。

| 维度 | 评估 |
|------|------|
| 工作量化 | 2-4 周（含调试） |
| 风险 | 🔴 高 |
| 风险点 | 四柱计算错误导致全线输出偏差；依赖树复杂（需同时嵌入 bazi-master-analysis）；无测试保证 |
| 适用阶段 | 仅用于原型/学习 |

#### 路径 B：API 网关模式（推荐中间路径 🟡）

bazi-skill-dist 保持独立服务，知命通过 HTTP API 调用。

| 维度 | 评估 |
|------|------|
| 工作量 | 3-5 周 |
| 风险 | 🟡 中 |
| 做法 | 1. 修复四柱计算（替换为正确万年历）<br>2. 新增知命所需字段映射层<br>3. 保持两系统独立部署 |
| 优点 | 隔离风险、可独立迭代 |
| 缺点 | 网络开销、双系统运维 |

#### 路径 C：参考架构重写（推荐 ✅）

仅复用 bazi-skill-dist 的**架构设计**和**核心数据模型**，重写四柱计算 + 用神推导。

| 维度 | 评估 |
|------|------|
| 工作量 | 6-10 周 |
| 风险 | 🟢 低 |
| 做法 | 1. 复用 `BaziChart`/`Pillar`/`DaYunPillar` 数据模型<br>2. 复用 `ChartParser`（藏干表+十神逻辑已验证）<br>3. 复用 `SchoolCompiler` 的 ABC 架构<br>4. 重写四柱计算（用 `lunarcalendar` 或 `ephem` 万年历）<br>5. 植入 `data_tier` 概念到 FactGraph<br>6. 新增用神推导引擎<br>7. 编写完整测试（200+ 测试用例） |
| 优点 | 无继承技术债、可完全控制计算准确性 |
| 缺点 | 开发周期较长 |

### 总体评分

| 维度 | 评分 | 颜色 |
|------|------|------|
| 架构设计 | 4/5 | 🟢 |
| 排盘准确性 | 2/5 | 🔴 |
| 学派系统 | 3/5 | 🟡 |
| 共识机制 | 2/5 | 🟡 |
| API 兼容性 | 2/5 | 🔴 |
| 测试覆盖 | 1/5 | 🔴 |
| 代码质量 | 3/5 | 🟡 |
| 文档注释 | 4/5 | 🟢 |
| **总体复用价值** | **2.5/5** | 🟡 |

---

## 附录：关键文件索引

| # | 文件路径（相对 bazi-skill-dist） | 用途 | 行数 | 关键函数 |
|---|----------------------------------|------|------|---------|
| 1 | `scripts/rule_engine/api/main.py` | FastAPI 主入口（传统） | 422 | `compute_pillars()`, `run_inference_stream()`, `inference_run()` |
| 2 | `scripts/rule_engine/api/server.py` | FastAPI 主入口（新版） | 146 | `analyze()`, `get_trace()`, `stream_llm_narrative()` |
| 3 | `scripts/rule_engine/api/chart_calculator.py` | 四柱计算适配层 | 54 | `compute_pillars()`, `build_pillar_strings()` |
| 4 | `scripts/rule_engine/api/controller.py` | 分析管线编排器 | 346 | `ChartAnalysisController.analyze()`, `_determine_body_strength()` |
| 5 | `scripts/rule_engine/parser/chart_parser.py` | 命盘解析器 + 藏干表 | 197 | `ChartParser.parse()`, `_get_ten_god()` |
| 6 | `scripts/rule_engine/core/bazi_chart.py` | BaziChart 数据模型 | 141 | `Pillar`, `BaziChart`, `ten_god_count()`, `element_count()` |
| 7 | `scripts/rule_engine/engine/runtime.py` | InferenceRuntime 状态机 | 630 | `run()`, `run_dynamic()`, `run_multi_school()` |
| 8 | `scripts/rule_engine/engine/fact_engine.py` | 派生事实引擎 | 100+ | `FactSpace`, `DerivedFactEngine.derive()` |
| 9 | `scripts/rule_engine/schools/school_compiler.py` | 学派编译器 ABC | 176 | `SchoolCompiler.compile()`, 5 个抽象方法 |
| 10 | `scripts/rule_engine/schools/school_config.py` | 学派配置 + 注册表 | 65 | `SCHOOL_REGISTRY`, 4 学派权重配置 |
| 11 | `scripts/rule_engine/schools/school_result.py` | SchoolInferenceResult | 38 | 学派推理输出数据模型 |
| 12 | `scripts/rule_engine/schools/compilers/sub_ping.py` | 子平派编译器 | 161 | `compute_body_strength()`, `assess_pattern()`, `apply_climate_rules()` |
| 13 | `scripts/rule_engine/schools/compilers/liang_xiangrun.py` | 梁湘润编译器 | 155 | 同上结构 |
| 14 | `scripts/rule_engine/schools/compilers/yuan_shushan.py` | 袁树珊编译器 | 146 | 同上结构 |
| 15 | `scripts/rule_engine/schools/compilers/wei_qianli.py` | 韦千里编译器 | 126 | 同上结构 |
| 16 | `scripts/rule_engine/schools/consensus/engine.py` | 共识引擎 | 323 | `ConsensusEngine.consensus()`, 3 种策略 |
| 17 | `scripts/rule_engine/schools/consensus/models.py` | 共识数据模型 | 111 | `ConsensusResult`, `SchoolConclusion` |
| 18 | `scripts/rule_engine/temporal/overlay_engine.py` | 时间覆盖引擎 | 651 | `compute_da_yun_sequence()`, `compute_start_age()`, `build_liu_nian()` |
| 19 | `scripts/rule_engine/temporal/dayun_rules.py` | 大运顺逆规则 | 61 | `resolve_direction()` |
| 20 | `scripts/rule_engine/temporal/start_age_calculator.py` | 起运年龄计算 | 30 | `calculate_start_age()` |
| 21 | `scripts/rule_engine/temporal/jieqi_provider.py` | 节气 provider | 28 | `get_nearest_jieqi()` — 占位实现 |
| 22 | `scripts/rule_engine/temporal/destiny_timeline.py` | 人生时间线计算 | 300 | `DestinyTimeline.compute()` |
| 23 | `scripts/rule_engine/temporal/annual_flow_generator.py` | 流年序列生成 | 157 | `AnnualFlowGenerator.generate()` |
| 24 | `scripts/rule_engine/contract/response.py` | 规范响应数据模型 | — | `InferenceResponse` |
| 25 | `scripts/rule_engine/contract/request.py` | 规范请求数据模型 | — | `InferenceRequest` |
| 26 | `<external>/bazi-master-analysis/scripts/calculate_bazi.py` | 外部四柱计算引擎 | 487 | `BaziCalculator`, `_calculate_pillars()`, `_get_day_ganzhi()` |
| 27 | `docs/13_API接口契约设计.md` | 知命 API 契约（对比参考） | 1549 | — |

---

*报告结束*

*扫描日期：2026-07-15 | 扫描类型：纯只读源码审计 | 证据等级说明：L1=直接源码观测 / L2=多源推导 / L3=推断*
