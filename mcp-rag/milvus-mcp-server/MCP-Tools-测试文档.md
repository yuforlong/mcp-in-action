# MCP API 测试文档

本文档提供 Milvus MCP 服务器四个主要 API 端点的测试指南：`storeKnowledge`、`searchKnowledge`、`storeFAQ` 和 `searchFAQ`。

## 测试环境

- 基础 URL: `http://localhost:8080/api/v1`
- 请求内容类型: `application/json`

## 1. storeKnowledge API

### 端点
```
POST /api/v1/storeKnowledge
```

### 功能描述
存储文档到知识库中，以便后续检索。

### 请求参数

```json
{
  "content": "这是一个关于Python编程的知识文档。Python是一种面向对象的解释型编程语言，由吉多·范罗苏姆创建于1989年底。Python是纯粹的自由软件，源代码和解释器CPython遵循GPL（GNU General Public License）协议。Python语法简洁而清晰，具有丰富而强大的类库，常被称为胶水语言，可以把用其他语言制作的各种模块很轻松地联结在一起。",
  "metadata": {
    "title": "Python基础知识",
    "author": "萤火AI百宝箱",
    "category": "编程",
    "tags": ["Python", "编程语言", "基础知识"]
  }
}
```

| 参数 | 类型 | 是否必需 | 描述 |
|------|------|---------|------|
| content | string | 是 | 文档内容，使用自然语言描述 |
| metadata | object | 否 | 文档相关的元数据，可存储任意键值对信息 |

### 响应
- 状态码: `201 Created` - 成功存储文档
- 响应体: 无

### 测试样例

```bash
curl -X POST "http://localhost:8080/api/v1/storeKnowledge" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "这是一个关于Python编程的知识文档。Python是一种面向对象的解释型编程语言，由吉多·范罗苏姆创建于1989年底。Python是纯粹的自由软件，源代码和解释器CPython遵循GPL（GNU General Public License）协议。Python语法简洁而清晰，具有丰富而强大的类库，常被称为胶水语言，可以把用其他语言制作的各种模块很轻松地联结在一起。",
           "metadata": {
             "title": "Python基础知识",
             "author": "萤火AI百宝箱",
             "category": "编程",
             "tags": ["Python", "编程语言", "基础知识"]
           }
         }'
```

## 2. searchKnowledge API

### 端点
```
POST /api/v1/searchKnowledge
```

### 功能描述
在知识库中搜索与查询语句语义相似的文档。

### 请求参数

```json
{
  "query": "Python编程语言有哪些特点?",
  "size": 5
}
```

| 参数 | 类型 | 是否必需 | 描述 |
|------|------|---------|------|
| query | string | 是 | 查询语句，描述想要查找的内容 |
| size | integer | 否 | 返回结果数量，默认为20 |

### 响应
- 状态码: `200 OK` - 查询成功
- 响应体: 匹配文档列表，每个文档包含 content 和 metadata

```json
[
  {
    "content": "这是一个关于Python编程的知识文档。Python是一种面向对象的解释型编程语言，由吉多·范罗苏姆创建于1989年底。Python是纯粹的自由软件，源代码和解释器CPython遵循GPL（GNU General Public License）协议。Python语法简洁而清晰，具有丰富而强大的类库，常被称为胶水语言，可以把用其他语言制作的各种模块很轻松地联结在一起。",
    "metadata": {
      "title": "Python基础知识",
      "author": "萤火AI百宝箱",
      "category": "编程",
      "tags": ["Python", "编程语言", "基础知识"]
    }
  },
  // 更多匹配文档...
]
```

### 测试样例

```bash
curl -X POST "http://localhost:8080/api/v1/searchKnowledge" \
     -H "Content-Type: application/json" \
     -d '{
           "query": "Python编程语言有哪些特点?",
           "size": 5
         }'
```

## 3. storeFAQ API

### 端点
```
POST /api/v1/storeFAQ
```

### 功能描述
存储常见问题解答(FAQ)到FAQ库中，以便后续检索。

### 请求参数

```json
{
  "question": "如何在Python中创建一个虚拟环境?",
  "answer": "在Python中创建虚拟环境可以使用venv模块。首先，打开命令行终端，然后执行以下命令：\n\n```bash\npython -m venv myenv\n```\n\n其中myenv是虚拟环境的名称。创建完成后，使用以下命令激活虚拟环境：\n\n- Windows: `myenv\\Scripts\\activate`\n- macOS/Linux: `source myenv/bin/activate`\n\n激活后，终端提示符前会显示虚拟环境名称，表示当前处于虚拟环境中。",
    "metadata": {
      "title": "Python基础知识",
      "author": "萤火AI百宝箱",
      "category": "编程",
      "tags": ["Python", "编程语言", "基础知识"]
    }
}
```

| 参数 | 类型 | 是否必需 | 描述 |
|------|------|---------|------|
| question | string | 是 | FAQ问题内容 |
| answer | string | 是 | FAQ答案内容 |

### 响应
- 状态码: `201 Created` - 成功存储FAQ
- 响应体: 无

### 测试样例

```bash
curl -X POST "http://localhost:8080/api/v1/storeFAQ" \
     -H "Content-Type: application/json" \
     -d '{
           "question": "如何在Python中创建一个虚拟环境?",
           "answer": "在Python中创建虚拟环境可以使用venv模块。首先，打开命令行终端，然后执行以下命令：\n\n```bash\npython -m venv myenv\n```\n\n其中myenv是虚拟环境的名称。创建完成后，使用以下命令激活虚拟环境：\n\n- Windows: `myenv\\Scripts\\activate`\n- macOS/Linux: `source myenv/bin/activate`\n\n激活后，终端提示符前会显示虚拟环境名称，表示当前处于虚拟环境中。"
         }'
```

## 4. searchFAQ API

### 端点
```
POST /api/v1/searchFAQ
```

### 功能描述
在FAQ库中搜索与查询语句语义相似的问题和答案。

### 请求参数

```json
{
  "query": "怎么搭建Python隔离环境?",
  "size": 3
}
```

| 参数 | 类型 | 是否必需 | 描述 |
|------|------|---------|------|
| query | string | 是 | 查询语句，描述想要查找的问题 |
| size | integer | 否 | 返回结果数量，默认为20 |

### 响应
- 状态码: `200 OK` - 查询成功
- 响应体: 匹配的FAQ列表，每个FAQ包含question和answer

```json
[
  {
    "question": "如何在Python中创建一个虚拟环境?",
    "answer": "在Python中创建虚拟环境可以使用venv模块。首先，打开命令行终端，然后执行以下命令：\n\n```bash\npython -m venv myenv\n```\n\n其中myenv是虚拟环境的名称。创建完成后，使用以下命令激活虚拟环境：\n\n- Windows: `myenv\\Scripts\\activate`\n- macOS/Linux: `source myenv/bin/activate`\n\n激活后，终端提示符前会显示虚拟环境名称，表示当前处于虚拟环境中。"
  },
  // 更多匹配FAQ...
]
```

### 测试样例

```bash
curl -X POST "http://localhost:8080/api/v1/searchFAQ" \
     -H "Content-Type: application/json" \
     -d '{
           "query": "怎么搭建Python隔离环境?",
           "size": 3
         }'
```

## 批量测试示例

以下提供一个简单的Python脚本，用于批量测试这些API端点：

```python
import requests
import json

# 基础URL
BASE_URL = "http://localhost:8080/api/v1"

# 测试知识库存储
def test_store_knowledge():
    print("测试 storeKnowledge API...")
    knowledge_data = {
        "content": "这是一个关于Python编程的知识文档。Python是一种面向对象的解释型编程语言，由吉多·范罗苏姆创建于1989年底。Python是纯粹的自由软件，源代码和解释器CPython遵循GPL（GNU General Public License）协议。Python语法简洁而清晰，具有丰富而强大的类库，常被称为胶水语言，可以把用其他语言制作的各种模块很轻松地联结在一起。",
        "metadata": {
            "title": "Python基础知识",
            "author": "萤火AI百宝箱",
            "category": "编程",
            "tags": ["Python", "编程语言", "基础知识"]
        }
    }
    
    response = requests.post(f"{BASE_URL}/storeKnowledge", json=knowledge_data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 201:
        print("知识存储成功!")
    else:
        print(f"错误: {response.text}")
    print("-" * 50)

# 测试知识库搜索
def test_search_knowledge():
    print("测试 searchKnowledge API...")
    search_data = {
        "query": "Python编程语言有哪些特点?",
        "size": 5
    }
    
    response = requests.post(f"{BASE_URL}/searchKnowledge", json=search_data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        results = response.json()
        print(f"找到 {len(results)} 条匹配结果:")
        for i, result in enumerate(results, 1):
            print(f"结果 {i}:")
            print(f"内容: {result['content'][:100]}...")
            print(f"元数据: {json.dumps(result['metadata'], ensure_ascii=False)}")
            print()
    else:
        print(f"错误: {response.text}")
    print("-" * 50)

# 测试FAQ存储
def test_store_faq():
    print("测试 storeFAQ API...")
    faq_data = {
        "question": "如何在Python中创建一个虚拟环境?",
        "answer": "在Python中创建虚拟环境可以使用venv模块。首先，打开命令行终端，然后执行以下命令：\n\n```bash\npython -m venv myenv\n```\n\n其中myenv是虚拟环境的名称。创建完成后，使用以下命令激活虚拟环境：\n\n- Windows: `myenv\\Scripts\\activate`\n- macOS/Linux: `source myenv/bin/activate`\n\n激活后，终端提示符前会显示虚拟环境名称，表示当前处于虚拟环境中。"
    }
    
    response = requests.post(f"{BASE_URL}/storeFAQ", json=faq_data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 201:
        print("FAQ存储成功!")
    else:
        print(f"错误: {response.text}")
    print("-" * 50)

# 测试FAQ搜索
def test_search_faq():
    print("测试 searchFAQ API...")
    search_data = {
        "query": "怎么搭建Python隔离环境?",
        "size": 3
    }
    
    response = requests.post(f"{BASE_URL}/searchFAQ", json=search_data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        results = response.json()
        print(f"找到 {len(results)} 条匹配结果:")
        for i, result in enumerate(results, 1):
            print(f"结果 {i}:")
            print(f"问题: {result['question']}")
            print(f"答案: {result['answer'][:100]}...")
            print()
    else:
        print(f"错误: {response.text}")
    print("-" * 50)

if __name__ == "__main__":
    # 按顺序执行测试
    test_store_knowledge()
    test_search_knowledge()
    test_store_faq()
    test_search_faq()
```

## 测试注意事项

1. 确保 MCP 服务器已正确启动，并在 `http://localhost:8080` 运行
2. 测试 `searchKnowledge` 前，确保已使用 `storeKnowledge` 存储了相关知识
3. 测试 `searchFAQ` 前，确保已使用 `storeFAQ` 存储了相关FAQ
4. 向量嵌入模型会影响搜索结果，确保使用适合的嵌入模型 