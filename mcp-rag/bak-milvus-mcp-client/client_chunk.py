from markdown_it import MarkdownIt

def parse_markdown_to_ast(markdown_text):
    """
    将Markdown文本解析为抽象语法树(AST)
    
    参数:
        markdown_text: 输入的Markdown文本
    
    返回:
        tokens: Markdown解析后的令牌列表
        md: MarkdownIt实例
    """
    md = MarkdownIt()
    tokens = md.parse(markdown_text)
    return tokens, md

def get_token_text(token):
    """
    从令牌中提取文本内容
    
    参数:
        token: Markdown令牌
    
    返回:
        文本内容字符串
    """
    if token.type == "inline":
        # 对于内联类型的令牌，连接其所有子令牌的内容
        return "".join(child.content for child in token.children if hasattr(child, "content"))
    elif token.type in ["paragraph_open", "paragraph_close"]:
        # 段落的开始和结束标记不包含文本内容
        return ""
    else:
        # 其他类型的令牌，直接返回其内容
        return token.content or ""

def split_ast_by_size(tokens, max_size):
    """
    按照最大大小将AST令牌列表分割成多个块
    
    参数:
        tokens: 令牌列表
        max_size: 每个块的最大文本长度
    
    返回:
        分割后的块列表，每个块包含一组令牌
    """
    chunks = []
    current_chunk = []
    current_size = 0

    for token in tokens:
        # 获取当前令牌的文本内容并计算其大小
        token_text = get_token_text(token)
        token_size = len(token_text)

        # 如果添加当前令牌会超过最大大小，则创建新块
        if current_size + token_size > max_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_size = 0

        # 将令牌添加到当前块中
        current_chunk.append(token)
        current_size += token_size

    # 确保最后一个块也被添加到结果中
    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def tokens_to_markdown(tokens, md):
    """
    将令牌列表渲染回Markdown文本
    
    参数:
        tokens: 令牌列表
        md: MarkdownIt实例
    
    返回:
        渲染后的Markdown文本
    """
    return md.renderer.render(tokens, md.options, {})

def process_markdown(markdown_text, max_size):
    """
    处理Markdown文本，将其分割成多个块
    
    参数:
        markdown_text: 输入的Markdown文本
        max_size: 每个块的最大文本长度
    
    返回:
        分割后的Markdown文本块列表
    """
    # 将Markdown解析为AST
    tokens, md = parse_markdown_to_ast(markdown_text)
    # 按大小分割AST
    chunks = split_ast_by_size(tokens, max_size)
    # 将每个块渲染回Markdown文本
    return [tokens_to_markdown(chunk, md) for chunk in chunks]

def to_chunks(markdown_text, max_size):
    """
    将Markdown文本分割成指定大小的块的主函数
    
    参数:
        markdown_text: 输入的Markdown文本
        max_size: 每个块的最大文本长度
    
    返回:
        分割后的Markdown文本块列表
    """
    chunks = process_markdown(markdown_text, max_size)
    return chunks 