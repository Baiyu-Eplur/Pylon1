import os

def search_keyword_in_tcl_files(root_path, keyword):
    matched_files = []

    for foldername, subfolders, filenames in os.walk(root_path):
        for filename in filenames:
            if filename.endswith(".m"):
                full_path = os.path.join(foldername, filename)
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if keyword in content:
                            matched_files.append(full_path)
                except Exception as e:
                    print(f"无法读取文件 {full_path}，错误：{e}")

    return matched_files

if __name__ == "__main__":
    # 用户输入部分
    search_path = 'D:\\Uob\\Tower Pylon\\TIMUR2'
    keyword = 'Reaction.out'

    results = search_keyword_in_tcl_files(search_path, keyword)

    print("\n搜索结果：")
    if results:
        for filepath in results:
            print(filepath)
    else:
        print("未找到包含关键词的文件。")
