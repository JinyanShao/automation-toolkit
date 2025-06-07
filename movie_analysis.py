# 导入 pandas 库，通常简写为 pd
import pandas as pd
import json # 导入 json 模块，用于处理 JSON 格式的字符串

# 导入可视化库
import matplotlib.pyplot as plt
import seaborn as sns

# 设置 Matplotlib 和 Seaborn 的样式，让图表更美观
# 解决中文显示问题（Mac）
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] 
plt.rcParams['axes.unicode_minus'] = False # 解决负号显示问题
sns.set_style("whitegrid") # 设置网格风格

# 定义数据集文件的路径
# 确保 'tmdb_5000_movies.csv' 文件在和这个 Python 文件相同的目录中
file_path = 'tmdb_5000_movies.csv'

# 使用 pandas 的 read_csv 函数加载数据集
print("正在加载电影数据...")
try:
    movies_df = pd.read_csv(file_path)
    print("电影数据加载完成！")
except FileNotFoundError:
    print(f"错误：文件 '{file_path}' 未找到。请确认文件已下载并放置在正确位置。")
    # 如果文件找不到，程序就无法继续，所以我们在这里退出
    exit() 
except Exception as e:
    print(f"加载文件时发生未知错误：{e}")
    exit()

# --- 新增代码：打印所有列名 (用于调试，你可以保留或注释掉) ---
print("\n--- 数据集的所有列名 (movies_df.columns) ---")
print(movies_df.columns)
# --- 新增代码结束 ---

# 初步查看数据：显示 DataFrame 的前5行
print("\n--- 数据集的前5行 (movies_df.head()) ---")
print(movies_df.head())

# 初步查看数据：显示 DataFrame 的基本信息
print("\n--- 数据集的基本信息 (movies_df.info()) ---")
movies_df.info()

# 初步查看数据：显示 DataFrame 的统计摘要
print("\n--- 数据集的统计摘要 (movies_df.describe()) ---")
print(movies_df.describe())

# 初步查看数据：显示数据集的形状（行数和列数）
print(f"\n--- 数据集的形状 (行数, 列数): {movies_df.shape} ---")

# --- 数据清洗：处理缺失值 ---
print("\n--- 正在处理缺失值 ---")

# 1. 检查每列的缺失值数量 (处理前)
print("\n--- 缺失值检查 (处理前) ---")
print(movies_df.isnull().sum())

# 2. 处理 'runtime' (运行时长) 列的缺失值
initial_rows = movies_df.shape[0] 
movies_df.dropna(subset=['runtime'], inplace=True)
print(f"\n已删除 'runtime' 列缺失的行。处理前 {initial_rows} 行，处理后 {movies_df.shape[0]} 行。")

# 3. 处理 'release_date' (上映日期) 列的缺失值
initial_rows = movies_df.shape[0]
movies_df.dropna(subset=['release_date'], inplace=True)
print(f"已删除 'release_date' 列缺失的行。处理前 {initial_rows} 行，处理后 {movies_df.shape[0]} 行。")

# 4. 处理 'tagline' (宣传语) 列的缺失值
movies_df['tagline'].fillna('', inplace=True)
print("\n已用空字符串填充 'tagline' 列的缺失值。")

# 5. 再次检查所有列的缺失值数量，确认处理效果
print("\n--- 缺失值检查 (处理后) ---")
print(movies_df.isnull().sum())

print("缺失值处理完成！")

# --- 数据清洗：处理复杂列 (例如 'genres' 列) ---
print("\n--- 正在处理 'genres' 列 ---")

# 定义一个函数，用于解析 JSON 字符串并提取 'name' 字段
def parse_json_names(json_string):
    """
    解析 JSON 字符串，并提取其中所有字典的 'name' 字段，返回一个列表。
    如果字符串无效或为空，返回空列表。
    """
    if pd.isna(json_string) or json_string == '':
        return []
    try:
        list_of_dicts = json.loads(json_string)
        return [item['name'] for item in list_of_dicts]
    except json.JSONDecodeError:
        return []
    except TypeError:
        return []

# 对 'genres' 列应用这个函数
movies_df['genres_parsed'] = movies_df['genres'].apply(parse_json_names)
print("\n已从 'genres' 列中提取出电影类型名称。")

# 查看处理后的 'genres_parsed' 列的前5行，和原 'genres' 列对比
print("\n--- 'genres' 列处理前后对比 (前5行) ---")
print("原始 'genres' 列:")
print(movies_df['genres'].head())
print("\n处理后 'genres_parsed' 列:")
print(movies_df['genres_parsed'].head())

# 进一步分析电影类型分布 (仅作初步展示)
print("\n--- 电影类型分布 (前10位) ---")
print(movies_df['genres_parsed'].explode().value_counts().head(10))

print("\n'genres' 列处理完成！")

# --- 数据清洗：处理日期列 'release_date' ---
print("\n--- 正在处理 'release_date' 列 ---")

# 将 'release_date' 列转换为日期时间类型
movies_df['release_date_parsed'] = pd.to_datetime(movies_df['release_date'], errors='coerce')
print("\n已将 'release_date' 列转换为日期时间类型。")

# 提取年份
movies_df['release_year'] = movies_df['release_date_parsed'].dt.year
print("已从 'release_date' 中提取出年份。")

# 检查转换后的列和提取的年份
print("\n--- 'release_date' 和 'release_year' 列前5行 ---")
print(movies_df[['release_date', 'release_date_parsed', 'release_year']].head())

# 检查缺失值 (如果有新的NaT出现)
print("\n--- 转换后 'release_date_parsed' 缺失值检查 ---")
print(movies_df['release_date_parsed'].isnull().sum())

print("'release_date' 列处理完成！")

# --- 数据清洗：处理其他复杂列 ---
print("\n--- 正在处理 'keywords', 'production_companies', 'cast', 'crew' 等复杂列 ---")

# 定义需要解析的复杂列列表
complex_columns_to_parse = [
    'keywords',
    'production_companies',
    'cast', # 包含电影的主要演员信息
    'crew', # 包含电影的制作团队信息（如导演）
    'spoken_languages', # 电影使用的语言
    'production_countries' # 电影的制片国家
]

# 遍历并解析这些复杂列
for col in complex_columns_to_parse:
    if col in movies_df.columns: # 检查列是否存在于 DataFrame 中
        movies_df[f'{col}_parsed'] = movies_df[col].apply(parse_json_names)
        print(f"已从 '{col}' 列中提取出名称，新列为 '{col}_parsed'。")
        print(f"\n--- '{col}_parsed' 列前5行 ---")
        print(movies_df[f'{col}_parsed'].head())
    else:
        print(f"警告：列 '{col}' 不存在于数据集中，已跳过解析。")

print("\n所有复杂列处理完成！")

# --- 特征工程：计算电影利润 ---
print("\n--- 正在计算电影利润 ---")

# 电影利润 = 收入 - 预算
# 注意：原始数据中 budget 和 revenue 可能有 0 值，这表示缺失数据，而不是真实为 0
# 我们这里不做特殊处理，直接计算，但在实际分析时需要注意
movies_df['profit'] = movies_df['revenue'] - movies_df['budget']
print("已计算电影利润，新列为 'profit'。")

# 查看利润最高的前5部电影
print("\n--- 利润最高的电影 (前5部) ---")
print(movies_df[['title', 'budget', 'revenue', 'profit']].sort_values(by='profit', ascending=False).head())

print("\n电影利润计算完成！")

# --- 数据可视化：电影类型分布 ---
print("\n--- 正在绘制电影类型分布图 ---")

# 统计电影类型分布（你之前已经做过，这里复用结果）
genre_counts = movies_df['genres_parsed'].explode().value_counts().head(10)

# 创建条形图
plt.figure(figsize=(12, 6)) # 设置图表大小 (宽度, 高度)
sns.barplot(x=genre_counts.index, y=genre_counts.values, palette='viridis') # 使用 Seaborn 绘制条形图
plt.title('电影类型分布 (前10位)') # 设置图表标题
plt.xlabel('电影类型') # 设置 X 轴标签
plt.ylabel('电影数量') # 设置 Y 轴标签
plt.xticks(rotation=45, ha='right') # 旋转 X 轴标签，防止重叠
plt.tight_layout() # 自动调整图表布局，防止标签被截断

# 显示图表
plt.show() 
print("电影类型分布图绘制完成！")

# --- 数据可视化：电影利润分布 ---
print("\n--- 正在绘制电影利润分布图 ---")

# 过滤掉利润为0或负数的电影，只关注有正利润的电影（可选，但更直观）
# 否则0值太多会导致图表不清晰
profitable_movies = movies_df[movies_df['profit'] > 0]

# 创建利润分布的直方图
plt.figure(figsize=(12, 6))
# bins=50 表示将数据分成50个区间
# kde=True 表示在直方图上方绘制核密度估计曲线，显示数据的平滑分布
sns.histplot(data=profitable_movies, x='profit', bins=50, kde=True, palette='viridis') 
plt.title('电影利润分布 (只显示正利润电影)')
plt.xlabel('电影利润 (美元)')
plt.ylabel('电影数量')
# 设置X轴的显示格式为科学计数法，避免数字过长重叠
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0)) 
plt.tight_layout()

# 显示图表
plt.show()
print("电影利润分布图绘制完成！")
# --- 数据可视化：电影数量年度趋势 ---
print("\n--- 正在绘制电影数量年度趋势图 ---")

# 统计每年上映的电影数量
# .value_counts() 计算每个年份出现的次数
# .sort_index() 按年份（索引）进行排序
movies_per_year = movies_df['release_year'].value_counts().sort_index()

# 创建折线图
plt.figure(figsize=(15, 7))
sns.lineplot(x=movies_per_year.index, y=movies_per_year.values, marker='o', palette='viridis') # 使用 Seaborn 绘制折线图
plt.title('电影数量年度趋势')
plt.xlabel('年份')git init
plt.ylabel('电影数量')
plt.grid(True, linestyle='--', alpha=0.6) # 显示网格线
plt.tight_layout()

# 显示图表
plt.show()
print("电影数量年度趋势图绘制完成！")