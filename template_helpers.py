"""
安全的模板助手 - 为模板提供安全的数据访问
"""

def safe_get(data, path, default=None):
    """安全获取嵌套字典中的值"""
    try:
        keys = path.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return default
            if current is None:
                return default
        return current if current is not None else default
    except:
        return default

def safe_int(value, default=0):
    """安全转换为整数"""
    try:
        if isinstance(value, (int, float)):
            return int(value)
        elif isinstance(value, str):
            return int(value)
        else:
            return default
    except:
        return default

def safe_add(a, b, default=0):
    """安全相加"""
    try:
        return safe_int(a, 0) + safe_int(b, 0)
    except:
        return default

# 导出到模板全局变量
template_globals = {
    'safe_get': safe_get,
    'safe_int': safe_int,
    'safe_add': safe_add
}
