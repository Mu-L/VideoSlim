import os


def scan_directory(
    directory: str, extensions: list[str]
) -> tuple[list[str], list[str]]:
    """
    递归扫描指定目录，返回子文件夹列表和符合指定扩展名的文件列表

    Args:
        directory: 要扫描的根目录路径
        extensions: 要匹配的文件扩展名列表，必须包含点号（如[".mp4", ".avi"]），
                    匹配时不区分大小写

    Returns:
        tuple[list[str], list[str]]: 第一个元素是所有子文件夹的路径列表，
                                     第二个元素是符合扩展名的所有文件的路径列表

    该函数会：
    1. 扫描指定目录下的所有条目
    2. 将子文件夹和符合条件的文件分别添加到列表中
    3. 递归扫描每个子文件夹
    4. 返回完整的子文件夹列表和文件列表
    """
    subfolders, files = [], []

    for entry in os.scandir(directory):
        if entry.is_dir():
            subfolders.append(entry.path)
        elif entry.is_file() and os.path.splitext(entry.name)[1].lower() in extensions:
            files.append(entry.path)

    # Recursively scan subfolders
    for folder in list(subfolders):
        sf, f = scan_directory(folder, extensions)
        subfolders.extend(sf)
        files.extend(f)

    return subfolders, files
