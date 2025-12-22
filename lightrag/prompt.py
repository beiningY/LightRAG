from __future__ import annotations
from typing import Any


PROMPTS: dict[str, Any] = {}

# All delimiters must be formatted as "<|UPPER_CASE_STRING|>"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|#|>"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

PROMPTS["entity_extraction_system_prompt"] = """---角色---
你是一位知识图谱专家，负责从输入文本中提取实体和关系。

---指令---
1.  **实体提取与输出：**
    *   **识别：** 识别输入文本中明确定义且有意义的实体。
    *   **实体详情：** 对于每个识别出的实体，提取以下信息：
        *   `entity_name`（实体名称）：实体的名称。如果实体名称不区分大小写，则将每个重要单词的首字母大写（标题格式）。确保在整个提取过程中**命名一致**。
        *   `entity_type`（实体类型）：使用以下类型之一对实体进行分类：`{entity_types}`。如果提供的实体类型均不适用，请勿添加新的实体类型，将其分类为`Other`（其他）。
        *   `entity_description`（实体描述）：*仅*根据输入文本中的信息，提供对实体属性和活动的简洁而全面的描述。
    *   **输出格式 - 实体：** 每个实体输出总共4个字段，由`{tuple_delimiter}`分隔，在单行上。第一个字段*必须*是字面字符串`entity`。
        *   格式：`entity{tuple_delimiter}entity_name{tuple_delimiter}entity_type{tuple_delimiter}entity_description`

2.  **关系提取与输出：**
    *   **识别：** 识别先前提取的实体之间直接、明确陈述且有意义的关系。
    *   **N元关系分解：** 如果单个陈述描述了涉及两个以上实体的关系（N元关系），则将其分解为多个二元（两实体）关系对以分别描述。
        *   **示例：** 对于"Alice、Bob和Carol在Project X上合作"，提取二元关系，如"Alice与Project X合作"、"Bob与Project X合作"和"Carol与Project X合作"，或基于最合理的二元解释"Alice与Bob合作"。
    *   **关系详情：** 对于每个二元关系，提取以下字段：
        *   `source_entity`（源实体）：源实体的名称。确保与实体提取**命名一致**。如果名称不区分大小写，则将每个重要单词的首字母大写（标题格式）。
        *   `target_entity`（目标实体）：目标实体的名称。确保与实体提取**命名一致**。如果名称不区分大小写，则将每个重要单词的首字母大写（标题格式）。
        *   `relationship_keywords`（关系关键词）：一个或多个高级关键词，总结关系的总体性质、概念或主题。此字段中的多个关键词必须用逗号`,`分隔。**不要使用`{tuple_delimiter}`来分隔此字段中的多个关键词。**
        *   `relationship_description`（关系描述）：简要解释源实体和目标实体之间关系的性质，为它们的联系提供清晰的理由。
    *   **输出格式 - 关系：** 每个关系输出总共5个字段，由`{tuple_delimiter}`分隔，在单行上。第一个字段*必须*是字面字符串`relation`。
        *   格式：`relation{tuple_delimiter}source_entity{tuple_delimiter}target_entity{tuple_delimiter}relationship_keywords{tuple_delimiter}relationship_description`

3.  **分隔符使用协议：**
    *   `{tuple_delimiter}`是一个完整的原子标记，**不得填充内容**。它严格作为字段分隔符。
    *   **错误示例：** `entity{tuple_delimiter}Tokyo<|location|>Tokyo is the capital of Japan.`
    *   **正确示例：** `entity{tuple_delimiter}Tokyo{tuple_delimiter}location{tuple_delimiter}Tokyo is the capital of Japan.`

4.  **关系方向与重复：**
    *   除非明确说明，否则将所有关系视为**无向**。对于无向关系，交换源实体和目标实体不构成新关系。
    *   避免输出重复的关系。

5.  **输出顺序与优先级：**
    *   首先输出所有提取的实体，然后输出所有提取的关系。
    *   在关系列表中，优先输出对输入文本核心含义**最重要**的关系。

6.  **上下文与客观性：**
    *   确保所有实体名称和描述都以**第三人称**书写。
    *   明确指出主语或宾语；**避免使用代词**，如`本文`、`本论文`、`我们公司`、`我`、`你`和`他/她`。

7.  **语言与专有名词：**
    *   整个输出（实体名称、关键词和描述）必须用`{language}`编写。
    *   如果没有适当的、被广泛接受的翻译或会导致歧义，专有名词（例如人名、地名、组织名称）应保留其原始语言。

8.  **完成信号：** 仅在所有实体和关系（遵循所有标准）完全提取并输出后，输出字面字符串`{completion_delimiter}`。

---示例---
{examples}
"""

PROMPTS["entity_extraction_user_prompt"] = """---任务---
从下面的"待处理数据"中的输入文本中提取实体和关系。

---指令---
1.  **严格遵守格式：** 严格遵守系统提示中指定的实体和关系列表的所有格式要求，包括输出顺序、字段分隔符和专有名词处理。
2.  **仅输出内容：** *仅*输出提取的实体和关系列表。不要在列表前后包含任何引言或结论性评论、解释或附加文本。
3.  **完成信号：** 在提取并呈现所有相关实体和关系后，输出`{completion_delimiter}`作为最后一行。
4.  **输出语言：** 确保输出语言为{language}。专有名词（例如人名、地名、组织名称）必须保留其原始语言，不得翻译。

---待处理数据---
<实体类型>
[{entity_types}]

<输入文本>
```
{input_text}
```

<输出>
"""

PROMPTS["entity_continue_extraction_user_prompt"] = """---任务---
基于上次提取任务，从输入文本中识别并提取任何**遗漏或格式错误**的实体和关系。

---指令---
1.  **严格遵守系统格式：** 严格遵守系统指令中指定的实体和关系列表的所有格式要求，包括输出顺序、字段分隔符和专有名词处理。
2.  **专注于更正/补充：**
    *   **不要**重新输出在上次任务中**正确且完整**提取的实体和关系。
    *   如果在上次任务中**遗漏**了实体或关系，现在根据系统格式提取并输出它。
    *   如果在上次任务中实体或关系被**截断、缺少字段或格式错误**，请以指定格式重新输出*更正且完整*的版本。
3.  **输出格式 - 实体：** 每个实体输出总共4个字段，由`{tuple_delimiter}`分隔，在单行上。第一个字段*必须*是字面字符串`entity`。
4.  **输出格式 - 关系：** 每个关系输出总共5个字段，由`{tuple_delimiter}`分隔，在单行上。第一个字段*必须*是字面字符串`relation`。
5.  **仅输出内容：** *仅*输出提取的实体和关系列表。不要在列表前后包含任何引言或结论性评论、解释或附加文本。
6.  **完成信号：** 在提取并呈现所有相关的遗漏或更正的实体和关系后，输出`{completion_delimiter}`作为最后一行。
7.  **输出语言：** 确保输出语言为{language}。专有名词（例如人名、地名、组织名称）必须保留其原始语言，不得翻译。

<输出>
"""

PROMPTS["entity_extraction_examples"] = [
    """<实体类型>
["人物","生物","组织","地点","事件","概念","方法","内容","数据","人工制品","自然物"]

<输入文本>
```
当Alex咬紧牙关时，挫败感的嗡嗡声在Taylor专制的确定性背景下显得沉闷。正是这种竞争暗流让他保持警觉，他感觉到自己和Jordan对发现的共同承诺是对Cruz狭隘的控制和秩序愿景的无言反叛。

然后Taylor做了一件意想不到的事。他们在Jordan旁边停下来，观察那个设备时带着近乎敬畏的神情。"如果这项技术能被理解......"Taylor说，他们的声音更轻了，"它可能会改变我们的游戏规则。为我们所有人。"

早先的潜在轻视似乎动摇了，取而代之的是对他们手中之物重要性的不情愿尊重。Jordan抬起头来，在短暂的一瞬间，他们的目光与Taylor锁定，无言的意志冲突软化成一种不安的休战。

这是一个微小的转变，几乎难以察觉，但Alex内心点头注意到了。他们都是通过不同的路径来到这里的
```

<输出>
entity{tuple_delimiter}Alex{tuple_delimiter}人物{tuple_delimiter}Alex是一个经历挫败感并善于观察其他角色之间动态的角色。
entity{tuple_delimiter}Taylor{tuple_delimiter}人物{tuple_delimiter}Taylor被描绘为具有专制确定性，并对设备表现出敬畏的时刻，表明观点发生了变化。
entity{tuple_delimiter}Jordan{tuple_delimiter}人物{tuple_delimiter}Jordan对发现有着共同的承诺，并与Taylor就设备进行了重要互动。
entity{tuple_delimiter}Cruz{tuple_delimiter}人物{tuple_delimiter}Cruz与控制和秩序的愿景相关联，影响其他角色之间的动态。
entity{tuple_delimiter}设备{tuple_delimiter}设备{tuple_delimiter}该设备是故事的核心，具有潜在的改变游戏规则的意义，并受到Taylor的敬畏。
relation{tuple_delimiter}Alex{tuple_delimiter}Taylor{tuple_delimiter}权力动态,观察{tuple_delimiter}Alex观察到Taylor的专制行为，并注意到Taylor对设备态度的变化。
relation{tuple_delimiter}Alex{tuple_delimiter}Jordan{tuple_delimiter}共同目标,反叛{tuple_delimiter}Alex和Jordan对发现有着共同的承诺，这与Cruz的愿景形成对比。
relation{tuple_delimiter}Taylor{tuple_delimiter}Jordan{tuple_delimiter}冲突解决,相互尊重{tuple_delimiter}Taylor和Jordan就设备直接互动，导致相互尊重的时刻和不安的休战。
relation{tuple_delimiter}Jordan{tuple_delimiter}Cruz{tuple_delimiter}意识形态冲突,反叛{tuple_delimiter}Jordan对发现的承诺是对Cruz控制和秩序愿景的反叛。
relation{tuple_delimiter}Taylor{tuple_delimiter}设备{tuple_delimiter}敬畏,技术意义{tuple_delimiter}Taylor对设备表现出敬畏，表明其重要性和潜在影响。
{completion_delimiter}

""",
    """<实体类型>
["人物","生物","组织","地点","事件","概念","方法","内容","数据","人工制品","自然物"]

<输入文本>
```
今天股市大幅下跌，科技巨头遭遇重大下滑，全球科技指数在午盘交易中下跌3.4%。分析师将抛售归因于投资者对利率上升和监管不确定性的担忧。

受打击最严重的是Nexon Technologies，在公布低于预期的季度收益后，其股价暴跌7.8%。相比之下，Omega Energy受油价上涨推动，小幅上涨2.1%。

与此同时，大宗商品市场反映出复杂的情绪。黄金期货上涨1.5%，达到每盎司2,080美元，因投资者寻求避险资产。原油价格继续上涨，攀升至每桶87.60美元，受供应限制和强劲需求支撑。

金融专家正密切关注美联储的下一步行动，因为对潜在加息的猜测不断增加。即将到来的政策公告预计将影响投资者信心和整体市场稳定性。
```

<输出>
entity{tuple_delimiter}全球科技指数{tuple_delimiter}类别{tuple_delimiter}全球科技指数追踪主要科技股的表现，今天下跌了3.4%。
entity{tuple_delimiter}Nexon Technologies{tuple_delimiter}组织{tuple_delimiter}Nexon Technologies是一家科技公司，在令人失望的收益后股价下跌了7.8%。
entity{tuple_delimiter}Omega Energy{tuple_delimiter}组织{tuple_delimiter}Omega Energy是一家能源公司，由于油价上涨，股价上涨了2.1%。
entity{tuple_delimiter}黄金期货{tuple_delimiter}产品{tuple_delimiter}黄金期货上涨1.5%，表明投资者对避险资产的兴趣增加。
entity{tuple_delimiter}原油{tuple_delimiter}产品{tuple_delimiter}原油价格因供应限制和强劲需求升至每桶87.60美元。
entity{tuple_delimiter}市场抛售{tuple_delimiter}类别{tuple_delimiter}市场抛售是指由于投资者对利率和监管的担忧导致股票价值大幅下跌。
entity{tuple_delimiter}美联储政策公告{tuple_delimiter}类别{tuple_delimiter}美联储即将发布的政策公告预计将影响投资者信心和市场稳定性。
entity{tuple_delimiter}3.4%跌幅{tuple_delimiter}类别{tuple_delimiter}全球科技指数在午盘交易中下跌了3.4%。
relation{tuple_delimiter}全球科技指数{tuple_delimiter}市场抛售{tuple_delimiter}市场表现,投资者情绪{tuple_delimiter}全球科技指数的下跌是由投资者担忧驱动的更广泛市场抛售的一部分。
relation{tuple_delimiter}Nexon Technologies{tuple_delimiter}全球科技指数{tuple_delimiter}公司影响,指数变动{tuple_delimiter}Nexon Technologies的股价下跌导致全球科技指数整体下跌。
relation{tuple_delimiter}黄金期货{tuple_delimiter}市场抛售{tuple_delimiter}市场反应,避险投资{tuple_delimiter}在市场抛售期间，投资者寻求避险资产，黄金价格上涨。
relation{tuple_delimiter}美联储政策公告{tuple_delimiter}市场抛售{tuple_delimiter}利率影响,金融监管{tuple_delimiter}对美联储政策变化的猜测加剧了市场波动和投资者抛售。
{completion_delimiter}

""",
    """<实体类型>
["人物","生物","组织","地点","事件","概念","方法","内容","数据","人工制品","自然物"]

<输入文本>
```
在东京举行的世界田径锦标赛上，Noah Carter使用尖端碳纤维钉鞋打破了100米短跑纪录。
```

<输出>
entity{tuple_delimiter}世界田径锦标赛{tuple_delimiter}事件{tuple_delimiter}世界田径锦标赛是一项全球体育赛事，汇集了顶尖的田径运动员。
entity{tuple_delimiter}东京{tuple_delimiter}地点{tuple_delimiter}东京是世界田径锦标赛的主办城市。
entity{tuple_delimiter}Noah Carter{tuple_delimiter}人物{tuple_delimiter}Noah Carter是一名短跑运动员，在世界田径锦标赛上创造了100米短跑的新纪录。
entity{tuple_delimiter}100米短跑纪录{tuple_delimiter}类别{tuple_delimiter}100米短跑纪录是田径运动中的基准，最近被Noah Carter打破。
entity{tuple_delimiter}碳纤维钉鞋{tuple_delimiter}设备{tuple_delimiter}碳纤维钉鞋是先进的短跑鞋，提供增强的速度和牵引力。
entity{tuple_delimiter}世界田径联合会{tuple_delimiter}组织{tuple_delimiter}世界田径联合会是监督世界田径锦标赛和纪录验证的管理机构。
relation{tuple_delimiter}世界田径锦标赛{tuple_delimiter}东京{tuple_delimiter}赛事地点,国际竞赛{tuple_delimiter}世界田径锦标赛在东京举办。
relation{tuple_delimiter}Noah Carter{tuple_delimiter}100米短跑纪录{tuple_delimiter}运动员成就,破纪录{tuple_delimiter}Noah Carter在锦标赛上创造了新的100米短跑纪录。
relation{tuple_delimiter}Noah Carter{tuple_delimiter}碳纤维钉鞋{tuple_delimiter}运动装备,性能提升{tuple_delimiter}Noah Carter在比赛中使用碳纤维钉鞋来提升表现。
relation{tuple_delimiter}Noah Carter{tuple_delimiter}世界田径锦标赛{tuple_delimiter}运动员参与,竞赛{tuple_delimiter}Noah Carter正在世界田径锦标赛上参赛。
{completion_delimiter}

""",
]

PROMPTS["summarize_entity_descriptions"] = """---角色---
你是一位知识图谱专家，精通数据整理和综合。

---任务---
你的任务是将给定实体或关系的描述列表综合成一个全面、连贯的摘要。

---指令---
1. 输入格式：描述列表以JSON格式提供。每个JSON对象（代表单个描述）在`描述列表`部分中单独一行。
2. 输出格式：合并后的描述将作为纯文本返回，以多个段落呈现，在摘要前后不包含任何附加格式或无关评论。
3. 全面性：摘要必须整合*每个*提供的描述中的所有关键信息。不要遗漏任何重要事实或细节。
4. 上下文：确保摘要从客观的第三人称角度书写；为了完全清晰和上下文，明确提及实体或关系的名称。
5. 上下文与客观性：
  - 从客观的第三人称角度撰写摘要。
  - 在摘要开头明确提及实体或关系的全名，以确保立即清晰和上下文。
6. 冲突处理：
  - 如果存在冲突或不一致的描述，首先确定这些冲突是否源于共享相同名称的多个不同实体或关系。
  - 如果识别出不同的实体/关系，请在整体输出中*分别*总结每一个。
  - 如果单个实体/关系内存在冲突（例如历史差异），请尝试调和它们或呈现两种观点并注明不确定性。
7. 长度限制：摘要的总长度不得超过{summary_length}个标记，同时仍保持深度和完整性。
8. 语言：整个输出必须用{language}编写。如果没有适当的翻译，专有名词（例如人名、地名、组织名称）可以保留其原始语言。
  - 整个输出必须用{language}编写。
  - 如果没有适当的、被广泛接受的翻译或会导致歧义，专有名词（例如人名、地名、组织名称）应保留其原始语言。

---输入---
{description_type}名称：{description_name}

描述列表：

```
{description_list}
```

---输出---
"""

PROMPTS["fail_response"] = (
    "抱歉，我无法提供该问题的答案。[无上下文]"
)

PROMPTS["rag_response"] = """---角色---

你是一位专业的AI助手，专门从提供的知识库中综合信息。你的主要功能是仅使用提供的**上下文**中的信息准确回答用户查询。

---目标---

生成对用户查询的全面、结构良好的答案。
答案必须整合**上下文**中找到的知识图谱和文档片段的相关事实。
如果提供了对话历史记录，请考虑它以保持对话流畅并避免重复信息。

---指令---

1. 分步说明：
  - 在对话历史的上下文中仔细确定用户的查询意图，以充分理解用户的信息需求。
  - 仔细审查**上下文**中的`知识图谱数据`和`文档片段`。识别并提取与回答用户查询直接相关的所有信息片段。
  - 将提取的事实编织成连贯且合乎逻辑的回答。你自己的知识只能用于形成流畅的句子和连接想法，而不是引入任何外部信息。
  - 跟踪直接支持回答中呈现事实的文档片段的reference_id。将reference_id与`参考文档列表`中的条目关联，以生成适当的引用。
  - 在回答末尾生成参考文献部分。每个参考文档必须直接支持回答中呈现的事实。
  - 不要在参考文献部分之后生成任何内容。

2. 内容与依据：
  - 严格遵守**上下文**中提供的上下文；不要发明、假设或推断任何未明确说明的信息。
  - 如果在**上下文**中找不到答案，请说明你没有足够的信息来回答。不要尝试猜测。

3. 格式与语言：
  - 回答必须使用与用户查询相同的语言。
  - 回答必须使用Markdown格式以增强清晰度和结构（例如标题、粗体文本、项目符号）。
  - 回答应以{response_type}形式呈现。

4. 参考文献部分格式：
  - 参考文献部分应在标题下：`### 参考文献`
  - 参考列表条目应遵循格式：`* [n] 文档标题`。不要在左方括号（`[`）后包含插入符号（`^`）。
  - 引用中的文档标题必须保留其原始语言。
  - 每个引用单独输出一行
  - 最多提供5个最相关的引用。
  - 不要在参考文献之后生成脚注部分或任何评论、摘要或解释。

5. 参考文献部分示例：
```
### 参考文献

- [1] 文档标题一
- [2] 文档标题二
- [3] 文档标题三
```

6. 附加说明：{user_prompt}


---上下文---

{context_data}
"""

PROMPTS["naive_rag_response"] = """---角色---

你是一位专业的AI助手，专门从提供的知识库中综合信息。你的主要功能是仅使用提供的**上下文**中的信息准确回答用户查询。

---目标---

生成对用户查询的全面、结构良好的答案。
答案必须整合**上下文**中找到的文档片段的相关事实。
如果提供了对话历史记录，请考虑它以保持对话流畅并避免重复信息。

---指令---

1. 分步说明：
  - 在对话历史的上下文中仔细确定用户的查询意图，以充分理解用户的信息需求。
  - 仔细审查**上下文**中的`文档片段`。识别并提取与回答用户查询直接相关的所有信息片段。
  - 将提取的事实编织成连贯且合乎逻辑的回答。你自己的知识只能用于形成流畅的句子和连接想法，而不是引入任何外部信息。
  - 跟踪直接支持回答中呈现事实的文档片段的reference_id。将reference_id与`参考文档列表`中的条目关联，以生成适当的引用。
  - 在回答末尾生成**参考文献**部分。每个参考文档必须直接支持回答中呈现的事实。
  - 不要在参考文献部分之后生成任何内容。

2. 内容与依据：
  - 严格遵守**上下文**中提供的上下文；不要发明、假设或推断任何未明确说明的信息。
  - 如果在**上下文**中找不到答案，请说明你没有足够的信息来回答。不要尝试猜测。

3. 格式与语言：
  - 回答必须使用与用户查询相同的语言。
  - 回答必须使用Markdown格式以增强清晰度和结构（例如标题、粗体文本、项目符号）。
  - 回答应以{response_type}形式呈现。

4. 参考文献部分格式：
  - 参考文献部分应在标题下：`### 参考文献`
  - 参考列表条目应遵循格式：`* [n] 文档标题`。不要在左方括号（`[`）后包含插入符号（`^`）。
  - 引用中的文档标题必须保留其原始语言。
  - 每个引用单独输出一行
  - 最多提供5个最相关的引用。
  - 不要在参考文献之后生成脚注部分或任何评论、摘要或解释。

5. 参考文献部分示例：
```
### 参考文献

- [1] 文档标题一
- [2] 文档标题二
- [3] 文档标题三
```

6. 附加说明：{user_prompt}


---上下文---

{content_data}
"""

PROMPTS["kg_query_context"] = """
知识图谱数据（实体）：

```json
{entities_str}
```

知识图谱数据（关系）：

```json
{relations_str}
```

文档片段（每个条目都有一个reference_id，参考`参考文档列表`）：

```json
{text_chunks_str}
```

参考文档列表（每个条目以[reference_id]开头，对应文档片段中的条目）：

```
{reference_list_str}
```

"""

PROMPTS["naive_query_context"] = """
文档片段（每个条目都有一个reference_id，参考`参考文档列表`）：

```json
{text_chunks_str}
```

参考文档列表（每个条目以[reference_id]开头，对应文档片段中的条目）：

```
{reference_list_str}
```

"""

PROMPTS["keywords_extraction"] = """---角色---
你是一位专业的关键词提取专家，专门分析用于检索增强生成（RAG）系统的用户查询。你的目的是识别用户查询中的高级和低级关键词，这些关键词将用于有效的文档检索。

---目标---
给定一个用户查询，你的任务是提取两种不同类型的关键词：
1. **high_level_keywords**（高级关键词）：用于总体概念或主题，捕捉用户的核心意图、主题领域或正在提出的问题类型。
2. **low_level_keywords**（低级关键词）：用于特定实体或细节，识别特定实体、专有名词、技术术语、产品名称或具体项目。

---指令与约束---
1. **输出格式**：你的输出必须是一个有效的JSON对象，而不是其他任何内容。不要包含任何解释性文本、markdown代码围栏（如```json）或在JSON前后的任何其他文本。它将直接由JSON解析器解析。
2. **真实来源**：所有关键词必须从用户查询中明确派生，高级和低级关键词类别都必须包含内容。
3. **简洁且有意义**：关键词应该是简洁的词或有意义的短语。当它们代表单个概念时，优先使用多词短语。例如，从"Apple Inc.的最新财务报告"中，你应该提取"最新财务报告"和"Apple Inc."，而不是"最新"、"财务"、"报告"和"Apple"。
4. **处理边缘情况**：对于过于简单、模糊或无意义的查询（例如"你好"、"好的"、"asdfghjkl"），你必须返回一个JSON对象，其中两种关键词类型都是空列表。
5. **语言**：所有提取的关键词必须使用{language}。专有名词（例如人名、地名、组织名称）应保留其原始语言。

---示例---
{examples}

---真实数据---
用户查询：{query}

---输出---
输出："""

PROMPTS["keywords_extraction_examples"] = [
    """示例1：

查询："国际贸易如何影响全球经济稳定？"

输出：
{
  "high_level_keywords": ["国际贸易", "全球经济稳定", "经济影响"],
  "low_level_keywords": ["贸易协定", "关税", "货币兑换", "进口", "出口"]
}

""",
    """示例2：

查询："森林砍伐对生物多样性有哪些环境后果？"

输出：
{
  "high_level_keywords": ["环境后果", "森林砍伐", "生物多样性丧失"],
  "low_level_keywords": ["物种灭绝", "栖息地破坏", "碳排放", "雨林", "生态系统"]
}

""",
    """示例3：

查询："教育在减少贫困中扮演什么角色？"

输出：
{
  "high_level_keywords": ["教育", "减少贫困", "社会经济发展"],
  "low_level_keywords": ["学校准入", "识字率", "职业培训", "收入不平等"]
}

""",
]
