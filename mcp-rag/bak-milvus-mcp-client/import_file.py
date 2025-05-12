import os
import pdfplumber
from markdownify import markdownify as md

def pdf_to_markdown(pdf_path, output_md_path=None):
    """
    将PDF文件转换为Markdown格式
    
    Args:
        pdf_path: PDF文件路径
        output_md_path: 输出Markdown文件路径，如果为None则根据PDF路径生成
    
    Returns:
        输出的Markdown文件路径
    """
    if output_md_path is None:
        # 如果未指定输出路径，则使用PDF文件名并替换扩展名
        base_name = os.path.basename(pdf_path)
        name_without_ext = os.path.splitext(base_name)[0]
        output_md_path = os.path.join(os.path.dirname(pdf_path), f"{name_without_ext}.md")
    
    # 提取PDF中的文本
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
            text += "\n\n"  # 添加页面分隔符
    
    # 转换为Markdown格式
    markdown_text = md(text, heading_style="ATX")
    
    # 写入输出文件
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_text)
    
    return output_md_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_markdown.py <pdf_file_path> [output_md_path]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_md_path = sys.argv[2] if len(sys.argv) > 2 else None
    result_path = pdf_to_markdown(pdf_path, output_md_path)
    print(f"转换完成，输出文件: {result_path}") 