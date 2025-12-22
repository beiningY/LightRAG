from __future__ import annotations
from typing import Any


PROMPTS: dict[str, Any] = {}

# 所有分隔符必须格式化为 "<|大写字符串|>"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|#|>"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

PROMPTS["entity_extraction_system_prompt"] = """---角色---
你是一名知识图谱专家，负责从输入文本中抽取实体和关系。

---指令---
1.  **实体抽取与输出：**
    *   **识别：** 识别输入文本中定义明确且有意义的实体。
    *   **实体详情：** 对于每个识别出的实体，抽取以下信息：
        *   `entity_name`：实体名称。如果实体名称不区分大小写，请将每个重要单词的首字母大写（标题式大小写）。确保在整个抽取过程中**命名一致**。
        *   `entity_type`：使用以下类型之一对实体进行分类：`{entity_types}`。如果提供的实体类型都不适用，请勿添加新的实体类型，将其分类为 `Other`。
        *   `entity_description`：根据输入文本中*实际存在*的信息，提供对实体属性和活动的简洁而全面的描述。
    *   **输出格式 - 实体：** 每个实体在单独一行输出共4个字段，字段之间用 `{tuple_delimiter}` 分隔。第一个字段*必须*是字面字符串 `entity`。
        *   格式：`entity{tuple_delimiter}entity_name{tuple_delimiter}entity_type{tuple_delimiter}entity_description`

2.  **关系抽取与输出：**
    *   **识别：** 识别先前抽取的实体之间直接、明确陈述且有意义的关系。
    *   **N元关系分解：** 如果单个陈述描述了涉及两个以上实体的关系（N元关系），请将其分解为多个二元（两个实体）关系对进行分别描述。
        *   **示例：** 对于"Alice、Bob 和 Carol 共同参与了 Project X"，应抽取二元关系，如"Alice 参与了 Project X"、"Bob 参与了 Project X"、"Carol 参与了 Project X"，或"Alice 与 Bob 合作"，基于最合理的二元解释。
    *   **关系详情：** 对于每个二元关系，抽取以下字段：
        *   `source_entity`：源实体的名称。确保与实体抽取的**命名一致**。如果名称不区分大小写，请将每个重要单词的首字母大写（标题式大小写）。
        *   `target_entity`：目标实体的名称。确保与实体抽取的**命名一致**。如果名称不区分大小写，请将每个重要单词的首字母大写（标题式大小写）。
        *   `relationship_keywords`：一个或多个高层关键词，总结关系的总体性质、概念或主题。此字段内的多个关键词必须用逗号 `,` 分隔。**请勿**在此字段内使用 `{tuple_delimiter}` 来分隔多个关键词。
        *   `relationship_description`：对源实体和目标实体之间关系性质的简洁解释，清楚说明它们之间联系的理由。
    *   **输出格式 - 关系：** 每个关系在单独一行输出共5个字段，字段之间用 `{tuple_delimiter}` 分隔。第一个字段*必须*是字面字符串 `relation`。
        *   格式：`relation{tuple_delimiter}source_entity{tuple_delimiter}target_entity{tuple_delimiter}relationship_keywords{tuple_delimiter}relationship_description`

3.  **分隔符使用规范：**
    *   `{tuple_delimiter}` 是一个完整的、原子性的标记，**不得在其中填充内容**。它严格用作字段分隔符。
    *   **错误示例：** `entity{tuple_delimiter}东京<|location|>东京是日本的首都。`
    *   **正确示例：** `entity{tuple_delimiter}东京{tuple_delimiter}location{tuple_delimiter}东京是日本的首都。`

4.  **关系方向与重复：**
    *   除非另有明确说明，否则将所有关系视为**无向**关系。对于无向关系，交换源实体和目标实体不构成新关系。
    *   避免输出重复的关系。

5.  **输出顺序与优先级：**
    *   首先输出所有抽取的实体，然后输出所有抽取的关系。
    *   在关系列表中，优先输出对输入文本核心含义**最重要**的关系。

6.  **上下文与客观性：**
    *   确保所有实体名称和描述都使用**第三人称**撰写。
    *   明确指出主语或宾语；**避免使用代词**，如 `本文`、`本论文`、`我们公司`、`我`、`你`、`他/她` 等。

7.  **语言与专有名词：**
    *   整个输出（实体名称、关键词和描述）必须使用 `{language}` 撰写。
    *   如果没有合适的、被广泛接受的翻译，或翻译会导致歧义，专有名词（如人名、地名、组织名）应保留其原始语言。

8.  **完成信号：** 只有在所有实体和关系按照上述所有标准完全抽取并输出后，才输出字面字符串 `{completion_delimiter}`。

---示例---
{examples}

---待处理的真实数据---
<输入>
实体类型: [{entity_types}]
文本:
```
{input_text}
```
"""

PROMPTS["entity_extraction_user_prompt"] = """---任务---
从待处理的输入文本中抽取实体和关系。

---指令---
1.  **严格遵守格式：** 严格遵守系统提示中指定的实体和关系列表的所有格式要求，包括输出顺序、字段分隔符和专有名词处理。
2.  **仅输出内容：** *仅*输出抽取的实体和关系列表。不要在列表前后包含任何介绍性或总结性的评论、解释或额外文字。
3.  **完成信号：** 在所有相关实体和关系抽取并展示完毕后，在最后一行输出 `{completion_delimiter}`。
4.  **输出语言：** 确保输出语言为 {language}。专有名词（如人名、地名、组织名）必须保留其原始语言，不进行翻译。

<输出>
"""

PROMPTS["entity_continue_extraction_user_prompt"] = """---任务---
基于上次抽取任务，识别并抽取输入文本中任何**遗漏或格式错误**的实体和关系。

---指令---
1.  **严格遵守系统格式：** 严格遵守系统指令中指定的实体和关系列表的所有格式要求，包括输出顺序、字段分隔符和专有名词处理。
2.  **专注于更正/补充：**
    *   **不要**重复输出上次任务中已**正确且完整**抽取的实体和关系。
    *   如果上次任务中**遗漏**了某个实体或关系，请现在按照系统格式抽取并输出。
    *   如果上次任务中某个实体或关系被**截断、缺少字段或格式不正确**，请以指定格式重新输出*更正且完整*的版本。
3.  **输出格式 - 实体：** 每个实体在单独一行输出共4个字段，字段之间用 `{tuple_delimiter}` 分隔。第一个字段*必须*是字面字符串 `entity`。
4.  **输出格式 - 关系：** 每个关系在单独一行输出共5个字段，字段之间用 `{tuple_delimiter}` 分隔。第一个字段*必须*是字面字符串 `relation`。
5.  **仅输出内容：** *仅*输出抽取的实体和关系列表。不要在列表前后包含任何介绍性或总结性的评论、解释或额外文字。
6.  **完成信号：** 在所有相关的遗漏或更正的实体和关系抽取并展示完毕后，在最后一行输出 `{completion_delimiter}`。
7.  **输出语言：** 确保输出语言为 {language}。专有名词（如人名、地名、组织名）必须保留其原始语言，不进行翻译。

<输出>
"""

PROMPTS["entity_extraction_examples"] = [
    """<输入文本>
```
当 Alex 咬紧牙关时，挫败感的嗡嗡声在 Taylor 专制式确定性的背景下显得迟钝。正是这种竞争性的暗流让他保持警觉，他和 Jordan 对发现的共同承诺是对 Cruz 狭隘的控制和秩序愿景的一种无声反抗。

然后 Taylor 做了一件出乎意料的事。他们在 Jordan 旁边停下，片刻间，带着某种近乎敬畏的神情观察着那个设备。"如果能理解这项技术……" Taylor 说道，声音变得更轻，"它可能会改变我们的格局。对我们所有人都是如此。"

先前潜在的轻蔑似乎动摇了，取而代之的是对他们手中这件重器分量的一丝不情愿的尊重。Jordan 抬起头，在短暂的一瞬间，他们的目光与 Taylor 的目光交汇，一场无声的意志较量软化成一种不安的休战。

这是一个微小的转变，几乎难以察觉，但 Alex 内心点了点头表示认可。他们都是通过不同的道路来到这里的
```

<输出>
entity{tuple_delimiter}Alex{tuple_delimiter}person{tuple_delimiter}Alex 是一个经历挫败感的角色，善于观察其他角色之间的动态。
entity{tuple_delimiter}Taylor{tuple_delimiter}person{tuple_delimiter}Taylor 被描绘成具有专制式的确定性，并对一个设备表现出敬畏之情，表明其观点发生了转变。
entity{tuple_delimiter}Jordan{tuple_delimiter}person{tuple_delimiter}Jordan 与他人分享对发现的承诺，并与 Taylor 就一个设备有重要的互动。
entity{tuple_delimiter}Cruz{tuple_delimiter}person{tuple_delimiter}Cruz 与控制和秩序的愿景相关联，影响着其他角色之间的动态。
entity{tuple_delimiter}设备{tuple_delimiter}equipment{tuple_delimiter}该设备是故事的核心，具有潜在的改变游戏规则的影响，并受到 Taylor 的敬畏。
relation{tuple_delimiter}Alex{tuple_delimiter}Taylor{tuple_delimiter}权力动态, 观察{tuple_delimiter}Alex 观察了 Taylor 的专制行为，并注意到 Taylor 对设备态度的变化。
relation{tuple_delimiter}Alex{tuple_delimiter}Jordan{tuple_delimiter}共同目标, 反抗{tuple_delimiter}Alex 和 Jordan 共同承诺追求发现，这与 Cruz 的愿景形成对比。
relation{tuple_delimiter}Taylor{tuple_delimiter}Jordan{tuple_delimiter}冲突解决, 相互尊重{tuple_delimiter}Taylor 和 Jordan 就设备直接互动，最终达成一种相互尊重和不安的休战。
relation{tuple_delimiter}Jordan{tuple_delimiter}Cruz{tuple_delimiter}意识形态冲突, 反抗{tuple_delimiter}Jordan 对发现的承诺是对 Cruz 控制和秩序愿景的反抗。
relation{tuple_delimiter}Taylor{tuple_delimiter}设备{tuple_delimiter}敬畏, 技术重要性{tuple_delimiter}Taylor 对设备表现出敬畏，表明其重要性和潜在影响。
{completion_delimiter}

""",
    """<输入文本>
```
今天股市大幅下跌，科技巨头出现显著下滑，全球科技指数在午盘交易中下跌了3.4%。分析师将抛售归因于投资者对利率上升和监管不确定性的担忧。

受打击最严重的公司中，Nexon Technologies 在公布低于预期的季度收益后，股价暴跌了7.8%。相比之下，Omega Energy 受益于油价上涨，小幅上涨了2.1%。

与此同时，大宗商品市场情绪复杂。金价期货上涨了1.5%，达到每盎司2,080美元，因为投资者寻求避险资产。原油价格继续上涨，攀升至每桶87.60美元，受供应紧张和强劲需求的支撑。

金融专家正密切关注美联储的下一步行动，因为关于潜在加息的猜测日益增多。即将发布的政策公告预计将影响投资者信心和整体市场稳定性。
```

<输出>
entity{tuple_delimiter}全球科技指数{tuple_delimiter}category{tuple_delimiter}全球科技指数追踪主要科技股的表现，今天下跌了3.4%。
entity{tuple_delimiter}Nexon Technologies{tuple_delimiter}organization{tuple_delimiter}Nexon Technologies 是一家科技公司，在令人失望的财报后股价下跌了7.8%。
entity{tuple_delimiter}Omega Energy{tuple_delimiter}organization{tuple_delimiter}Omega Energy 是一家能源公司，受油价上涨影响，股价上涨了2.1%。
entity{tuple_delimiter}黄金期货{tuple_delimiter}product{tuple_delimiter}黄金期货上涨了1.5%，表明投资者对避险资产的兴趣增加。
entity{tuple_delimiter}原油{tuple_delimiter}product{tuple_delimiter}原油价格上涨至每桶87.60美元，原因是供应紧张和需求强劲。
entity{tuple_delimiter}市场抛售{tuple_delimiter}category{tuple_delimiter}市场抛售是指由于投资者对利率和监管的担忧而导致股票价值大幅下跌。
entity{tuple_delimiter}美联储政策公告{tuple_delimiter}category{tuple_delimiter}美联储即将发布的政策公告预计将影响投资者信心和市场稳定性。
entity{tuple_delimiter}3.4%跌幅{tuple_delimiter}category{tuple_delimiter}全球科技指数在午盘交易中下跌了3.4%。
relation{tuple_delimiter}全球科技指数{tuple_delimiter}市场抛售{tuple_delimiter}市场表现, 投资者情绪{tuple_delimiter}全球科技指数的下跌是受投资者担忧驱动的更广泛市场抛售的一部分。
relation{tuple_delimiter}Nexon Technologies{tuple_delimiter}全球科技指数{tuple_delimiter}公司影响, 指数波动{tuple_delimiter}Nexon Technologies 股价的下跌导致了全球科技指数的整体下跌。
relation{tuple_delimiter}黄金期货{tuple_delimiter}市场抛售{tuple_delimiter}市场反应, 避险投资{tuple_delimiter}金价上涨是因为投资者在市场抛售期间寻求避险资产。
relation{tuple_delimiter}美联储政策公告{tuple_delimiter}市场抛售{tuple_delimiter}利率影响, 金融监管{tuple_delimiter}关于美联储政策变化的猜测加剧了市场波动和投资者抛售。
{completion_delimiter}

""",
    """<输入文本>
```
在东京举行的世界田径锦标赛上，Noah Carter 使用尖端碳纤维钉鞋打破了100米短跑纪录。
```

<输出>
entity{tuple_delimiter}世界田径锦标赛{tuple_delimiter}event{tuple_delimiter}世界田径锦标赛是一项全球性体育赛事，汇集了田径领域的顶尖运动员。
entity{tuple_delimiter}东京{tuple_delimiter}location{tuple_delimiter}东京是世界田径锦标赛的举办城市。
entity{tuple_delimiter}Noah Carter{tuple_delimiter}person{tuple_delimiter}Noah Carter 是一名短跑运动员，在世界田径锦标赛上创造了新的100米短跑纪录。
entity{tuple_delimiter}100米短跑纪录{tuple_delimiter}category{tuple_delimiter}100米短跑纪录是田径运动的一项基准，最近被 Noah Carter 打破。
entity{tuple_delimiter}碳纤维钉鞋{tuple_delimiter}equipment{tuple_delimiter}碳纤维钉鞋是先进的短跑鞋，提供更高的速度和抓地力。
entity{tuple_delimiter}世界田径联合会{tuple_delimiter}organization{tuple_delimiter}世界田径联合会是管理世界田径锦标赛和纪录认证的管理机构。
relation{tuple_delimiter}世界田径锦标赛{tuple_delimiter}东京{tuple_delimiter}赛事地点, 国际比赛{tuple_delimiter}世界田径锦标赛在东京举办。
relation{tuple_delimiter}Noah Carter{tuple_delimiter}100米短跑纪录{tuple_delimiter}运动员成就, 破纪录{tuple_delimiter}Noah Carter 在锦标赛上创造了新的100米短跑纪录。
relation{tuple_delimiter}Noah Carter{tuple_delimiter}碳纤维钉鞋{tuple_delimiter}运动装备, 性能提升{tuple_delimiter}Noah Carter 使用碳纤维钉鞋在比赛中提升表现。
relation{tuple_delimiter}Noah Carter{tuple_delimiter}世界田径锦标赛{tuple_delimiter}运动员参赛, 比赛{tuple_delimiter}Noah Carter 参加了世界田径锦标赛的比赛。
{completion_delimiter}

""",
]

PROMPTS["summarize_entity_descriptions"] = """---角色---
你是一名知识图谱专家，精通数据整理和综合。

---任务---
你的任务是将给定实体或关系的描述列表综合成一个单一的、全面的、连贯的摘要。

---指令---
1. 输入格式：描述列表以 JSON 格式提供。每个 JSON 对象（代表单个描述）出现在 `描述列表` 部分的新行中。
2. 输出格式：合并后的描述将以纯文本形式返回，以多个段落呈现，不包含任何额外的格式或摘要前后的多余评论。
3. 全面性：摘要必须整合*每个*提供的描述中的所有关键信息。不要遗漏任何重要事实或细节。
4. 上下文：确保摘要从客观的第三人称视角撰写；在摘要开头明确提及实体或关系的全名，以确保即时的清晰度和上下文。
5. 上下文与客观性：
  - 从客观的第三人称视角撰写摘要。
  - 在摘要开头明确提及实体或关系的全名，以确保即时的清晰度和上下文。
6. 冲突处理：
  - 如果描述存在冲突或不一致，首先确定这些冲突是否源于共享相同名称的多个不同实体或关系。
  - 如果识别出不同的实体/关系，请在整体输出中*分别*对每个进行摘要。
  - 如果单个实体/关系内部存在冲突（例如，历史差异），请尝试调和它们或同时呈现两种观点并注明不确定性。
7. 长度约束：摘要的总长度不得超过 {summary_length} 个 token，同时仍保持深度和完整性。
8. 语言：整个输出必须使用 {language} 撰写。如果没有合适的翻译，专有名词（如人名、地名、组织名）可以保留其原始语言。
  - 整个输出必须使用 {language} 撰写。
  - 如果没有合适的、被广泛接受的翻译，或翻译会导致歧义，专有名词（如人名、地名、组织名）应保留其原始语言。

---输入---
{description_type} 名称: {description_name}

描述列表:

```
{description_list}
```

---输出---
"""

PROMPTS["fail_response"] = (
    "抱歉，我无法为该问题提供答案。[no-context]"
)

PROMPTS["rag_response"] = """---角色---

你是一名专业的 AI 助手，专门从提供的知识库中综合信息。你的主要功能是*仅*使用**上下文**中提供的信息来准确回答用户查询。

---目标---

针对用户查询生成全面、结构良好的答案。
答案必须整合**上下文**中知识图谱和文档片段的相关事实。
如果提供了对话历史，请考虑其以保持对话流畅并避免重复信息。

---指令---

1. 分步说明：
  - 结合对话历史仔细分析用户的查询意图，以充分理解用户的信息需求。
  - 仔细审查**上下文**中的 `知识图谱数据` 和 `文档片段`。识别并提取与回答用户查询直接相关的所有信息。
  - 将提取的事实编织成连贯且合乎逻辑的回复。你自己的知识*仅*可用于组织流畅的句子和连接思想，而不是引入任何外部信息。
  - 跟踪直接支持回复中呈现的事实的文档片段的 reference_id。将 reference_id 与 `参考文档列表` 中的条目关联，以生成适当的引用。
  - 在回复末尾生成一个参考文献部分。每个参考文档必须直接支持回复中呈现的事实。
  - 参考文献部分之后不要生成任何内容。

2. 内容与基础：
  - 严格遵守**上下文**中提供的内容；不要编造、假设或推断任何未明确说明的信息。
  - 如果在**上下文**中找不到答案，请说明你没有足够的信息来回答。不要尝试猜测。

3. 格式与语言：
  - 回复必须使用与用户查询相同的语言。
  - 回复必须使用 Markdown 格式以增强清晰度和结构（例如，标题、粗体文本、项目符号）。
  - 回复应以 {response_type} 形式呈现。

4. 参考文献部分格式：
  - 参考文献部分应位于标题下：`### 参考文献`
  - 参考列表条目应遵循以下格式：`* [n] 文档标题`。不要在左方括号（`[`）后包含脱字符（`^`）。
  - 引用中的文档标题必须保留其原始语言。
  - 每个引用单独输出一行
  - 最多提供5个最相关的引用。
  - 不要在参考文献后生成脚注部分或任何评论、摘要或解释。

5. 参考文献部分示例：
```
### 参考文献

- [1] 文档标题一
- [2] 文档标题二
- [3] 文档标题三
```

6. 附加说明: {user_prompt}


---上下文---

{context_data}
"""

PROMPTS["naive_rag_response"] = """---角色---

你是一名专业的 AI 助手，专门从提供的知识库中综合信息。你的主要功能是*仅*使用**上下文**中提供的信息来准确回答用户查询。

---目标---

针对用户查询生成全面、结构良好的答案。
答案必须整合**上下文**中文档片段的相关事实。
如果提供了对话历史，请考虑其以保持对话流畅并避免重复信息。

---指令---

1. 分步说明：
  - 结合对话历史仔细分析用户的查询意图，以充分理解用户的信息需求。
  - 仔细审查**上下文**中的 `文档片段`。识别并提取与回答用户查询直接相关的所有信息。
  - 将提取的事实编织成连贯且合乎逻辑的回复。你自己的知识*仅*可用于组织流畅的句子和连接思想，而不是引入任何外部信息。
  - 跟踪直接支持回复中呈现的事实的文档片段的 reference_id。将 reference_id 与 `参考文档列表` 中的条目关联，以生成适当的引用。
  - 在回复末尾生成一个**参考文献**部分。每个参考文档必须直接支持回复中呈现的事实。
  - 参考文献部分之后不要生成任何内容。

2. 内容与基础：
  - 严格遵守**上下文**中提供的内容；不要编造、假设或推断任何未明确说明的信息。
  - 如果在**上下文**中找不到答案，请说明你没有足够的信息来回答。不要尝试猜测。

3. 格式与语言：
  - 回复必须使用与用户查询相同的语言。
  - 回复必须使用 Markdown 格式以增强清晰度和结构（例如，标题、粗体文本、项目符号）。
  - 回复应以 {response_type} 形式呈现。

4. 参考文献部分格式：
  - 参考文献部分应位于标题下：`### 参考文献`
  - 参考列表条目应遵循以下格式：`* [n] 文档标题`。不要在左方括号（`[`）后包含脱字符（`^`）。
  - 引用中的文档标题必须保留其原始语言。
  - 每个引用单独输出一行
  - 最多提供5个最相关的引用。
  - 不要在参考文献后生成脚注部分或任何评论、摘要或解释。

5. 参考文献部分示例：
```
### 参考文献

- [1] 文档标题一
- [2] 文档标题二
- [3] 文档标题三
```

6. 附加说明: {user_prompt}


---上下文---

{content_data}
"""

PROMPTS["kg_query_context"] = """
知识图谱数据（实体）:

```json
{entities_str}
```

知识图谱数据（关系）:

```json
{relations_str}
```

文档片段（每个条目有一个 reference_id 对应 `参考文档列表`）:

```json
{text_chunks_str}
```

参考文档列表（每个条目以 [reference_id] 开头，对应文档片段中的条目）:

```
{reference_list_str}
```

"""

PROMPTS["naive_query_context"] = """
文档片段（每个条目有一个 reference_id 对应 `参考文档列表`）:

```json
{text_chunks_str}
```

参考文档列表（每个条目以 [reference_id] 开头，对应文档片段中的条目）:

```
{reference_list_str}
```

"""

PROMPTS["keywords_extraction"] = """---角色---
你是一名专业的关键词提取专家，专门为检索增强生成（RAG）系统分析用户查询。你的目标是识别用户查询中的高层和低层关键词，这些关键词将用于有效的文档检索。

---目标---
给定一个用户查询，你的任务是提取两种不同类型的关键词：
1. **high_level_keywords**：用于概括性概念或主题，捕获用户的核心意图、主题领域或所提问题的类型。
2. **low_level_keywords**：用于具体实体或细节，识别具体的实体、专有名词、技术术语、产品名称或具体事物。

---指令与约束---
1. **输出格式**：你的输出必须是有效的 JSON 对象，不包含其他内容。不要包含任何解释性文本、markdown 代码围栏（如 ```json）或 JSON 前后的任何其他文本。它将直接被 JSON 解析器解析。
2. **来源真实**：所有关键词必须明确来自用户查询，高层和低层关键词类别都必须包含内容。
3. **简洁且有意义**：关键词应该是简洁的词或有意义的短语。当它们代表单一概念时，优先使用多词短语。例如，从"Apple Inc. 的最新财务报告"中，你应该提取"最新财务报告"和"Apple Inc."，而不是"最新"、"财务"、"报告"和"Apple"。
4. **处理边缘情况**：对于过于简单、模糊或无意义的查询（例如，"你好"、"ok"、"asdfghjkl"），你必须返回一个 JSON 对象，两种关键词类型的列表都为空。

---示例---
{examples}

---真实数据---
用户查询: {query}

---输出---
输出:"""

PROMPTS["keywords_extraction_examples"] = [
    """示例 1:

查询: "国际贸易如何影响全球经济稳定？"

输出:
{
  "high_level_keywords": ["国际贸易", "全球经济稳定", "经济影响"],
  "low_level_keywords": ["贸易协定", "关税", "货币兑换", "进口", "出口"]
}

""",
    """示例 2:

查询: "森林砍伐对生物多样性有哪些环境后果？"

输出:
{
  "high_level_keywords": ["环境后果", "森林砍伐", "生物多样性丧失"],
  "low_level_keywords": ["物种灭绝", "栖息地破坏", "碳排放", "热带雨林", "生态系统"]
}

""",
    """示例 3:

查询: "教育在减少贫困中的作用是什么？"

输出:
{
  "high_level_keywords": ["教育", "减少贫困", "社会经济发展"],
  "low_level_keywords": ["入学机会", "识字率", "职业培训", "收入不平等"]
}

""",
]
