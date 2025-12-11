import os


def scan_directory(
    directory: str, extensions: list[str]
) -> tuple[list[str], list[str]]:
    """
    递归扫描目录，返回子文件夹和符合扩展名的文件列表

    Args:
        directory: 要扫描的目录路径
        extensions: 要包含的文件扩展名列表（不包含点号）

    Returns:
        包含子文件夹路径和符合扩展名的文件路径的元组
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
