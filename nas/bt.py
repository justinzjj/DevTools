"""
Author: Justin
Date: 2025-02-21 20:15:52
filename: 
version: 
Description: 
LastEditTime: 2025-02-21 20:18:14
"""

# 读取文件
with open("nas/tracker.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

# 删除空行并在每一行结尾添加逗号
processed_lines = [line.strip() + "," for line in lines if line.strip()]

# 将处理后的内容写回文件
with open("nas/tracker_processed.txt", "w", encoding="utf-8") as file:
    file.write("\n".join(processed_lines))

print("处理完成，结果已保存到 'tracker_processed.txt' 文件中。")
