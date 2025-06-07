# -*- coding: utf-8 -*-
# Python Foundational Project: Movie Data Analysis & Visualization
# This project performs comprehensive data loading, cleaning, analysis, and visualization
# of a movie dataset, highlighting key insights and trends.

# --- 1. Import necessary libraries ---
import pandas as pd # Data manipulation and analysis
import json # Handling JSON formatted strings within data
import matplotlib.pyplot as plt # Plotting library
import seaborn as sns # Enhanced plotting library for beautiful visualizations

# --- 2. Configuration for plotting (for better visualization and Chinese character support) ---
# Solve Chinese display issues (Mac)
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
# Solve negative sign display issues
plt.rcParams['axes.unicode_minus'] = False
# Set Seaborn style for better aesthetics
sns.set_style("whitegrid")

# --- 3. Define dataset file path ---
# Ensure 'tmdb_5000_movies.csv' file is in the same directory as this Python script
file_path = 'tmdb_5000_movies.csv'

# --- 4. Load the dataset ---
print("--- Loading movie data ---")
try:
    movies_df = pd.read_csv(file_path)
    print("Movie data loaded successfully!")
except FileNotFoundError:
    print(f"Error: File '{file_path}' not found. Please ensure the file is downloaded and placed in the correct location.")
    # Exit if file not found, as further operations depend on the data
    exit()
except Exception as e:
    print(f"An unknown error occurred while loading the file: {e}")
    exit()

print("\n--- Initial Data Overview (First 5 rows) ---")
print(movies_df.head())

print("\n--- Dataset Information (movies_df.info()) ---")
movies_df.info()

print("\n--- Statistical Summary (movies_df.describe()) ---")
print(movies_df.describe())

print(f"\n--- Dataset Shape (rows, columns): {movies_df.shape} ---")

# --- 5. Data Cleaning and Preprocessing ---
print("\n--- Starting data cleaning and preprocessing ---")

# Function to parse JSON strings and extract 'name' fields
def parse_json_names(json_string):
    """
    Parses a JSON string and extracts the 'name' field from all dictionaries within it.
    Returns an empty list if the string is invalid or empty.
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

# Handle missing values for 'runtime' and 'release_date' by dropping rows
initial_rows_count = movies_df.shape[0]
movies_df.dropna(subset=['runtime', 'release_date'], inplace=True)
print(f"\nDeleted rows with missing 'runtime' or 'release_date'. Rows before: {initial_rows_count}, rows after: {movies_df.shape[0]}.")

# Fill missing values for 'tagline' with empty strings
movies_df['tagline'].fillna('', inplace=True)
print("Filled missing values in 'tagline' column with empty strings.")

# Convert 'release_date' to datetime and extract 'release_year'
movies_df['release_date_parsed'] = pd.to_datetime(movies_df['release_date'], errors='coerce')
movies_df['release_year'] = movies_df['release_date_parsed'].dt.year
print("Converted 'release_date' to datetime and extracted 'release_year'.")

# Parse complex JSON columns
complex_columns_to_parse = [
    'genres', 'keywords', 'production_companies', 'cast', 'crew',
    'spoken_languages', 'production_countries'
]
for col in complex_columns_to_parse:
    if col in movies_df.columns:
        movies_df[f'{col}_parsed'] = movies_df[col].apply(parse_json_names)
        print(f"Parsed '{col}' column into '{col}_parsed'. (First 5 parsed: {movies_df[f'{col}_parsed'].head().tolist()})")
    else:
        print(f"Warning: Column '{col}' not found in dataset, skipped parsing.")

print("\nData cleaning and preprocessing completed!")

# --- 6. Feature Engineering ---
print("\n--- Starting feature engineering ---")

# Calculate 'profit'
# Note: 0 values in 'budget' and 'revenue' often indicate missing data, not true zero.
# For simplicity, we calculate directly; in real analysis, these need careful handling.
movies_df['profit'] = movies_df['revenue'] - movies_df['budget']
print("Calculated 'profit' column.")

print("\nFeature engineering completed!")

# --- 7. Data Analysis & Insights ---
# --- 7.5. 深入探索与关联性分析 (Deep Dive Exploration & Correlation) ---
print("\n--- 深入探索：电影预算、票房、评分和流行度之间的相关性 ---")

# 剔除 budget 或 revenue 为 0 的行，以便更准确地计算相关性
# 因为原始数据中 0 值往往代表缺失，而不是真实为 0
# 创建一个临时 DataFrame 用于相关性计算，避免修改原始df
df_for_corr = movies_df[(movies_df['budget'] > 0) & (movies_df['revenue'] > 0)].copy()

# 确保这些列是数值类型
df_for_corr['budget'] = pd.to_numeric(df_for_corr['budget'], errors='coerce')
df_for_corr['revenue'] = pd.to_numeric(df_for_corr['revenue'], errors='coerce')
df_for_corr['vote_average'] = pd.to_numeric(df_for_corr['vote_average'], errors='coerce')
df_for_corr['popularity'] = pd.to_numeric(df_for_corr['popularity'], errors='coerce')

# 计算相关性矩阵
correlation_matrix = df_for_corr[['budget', 'revenue', 'vote_average', 'popularity']].corr()

print("\n相关性矩阵 (Correlation Matrix):")
print(correlation_matrix)

# --- 数据可视化：相关性热力图 ---
print("\n--- 正在绘制相关性热力图 ---")
plt.figure(figsize=(10, 8))
# annot=True 表示在热力图上显示相关系数值
# fmt=".2f" 表示显示两位小数
# cmap='coolwarm' 设置颜色映射
sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', linewidths=.5)
plt.title('电影预算、票房、评分和流行度之间的相关性')
plt.tight_layout()
plt.savefig('correlation_matrix_heatmap.png') # 保存图表
plt.show()
print("相关性热力图绘制完成！")

# --- 数据可视化：散点图探索票房与评分/流行度关系 ---
print("\n--- 正在绘制票房与评分/流行度散点图 ---")

# 票房 vs 平均评分
plt.figure(figsize=(12, 7))
sns.scatterplot(x='vote_average', y='revenue', data=df_for_corr, alpha=0.6, s=50, hue='popularity', size='popularity', sizes=(20, 400), palette='viridis')
plt.title('电影票房与平均评分关系 (颜色和大小表示流行度)')
plt.xlabel('平均评分')
plt.ylabel('票房 (Revenue)')
plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0)) # 设置Y轴科学计数法
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('revenue_vs_vote_average_popularity.png') # 保存图表
plt.show()
print("票房与平均评分关系散点图绘制完成！")

# 票房 vs 流行度
plt.figure(figsize=(12, 7))
sns.scatterplot(x='popularity', y='revenue', data=df_for_corr, alpha=0.6, s=50, hue='vote_average', size='vote_average', sizes=(20, 400), palette='viridis')
plt.title('电影票房与流行度关系 (颜色和大小表示平均评分)')
plt.xlabel('流行度')
plt.ylabel('票房 (Revenue)')
plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('revenue_vs_popularity_vote_average.png') # 保存图表
plt.show()
print("票房与流行度关系散点图绘制完成！")
print("\n--- Performing data analysis ---")

# Find the order with the highest total sales (contextual to movie data)
print("\n--- Top 5 Most Profitable Movies ---")
print(movies_df[['title', 'profit', 'revenue', 'budget']].sort_values(by='profit', ascending=False).head())

# Analyze movie genre distribution
genre_counts = movies_df['genres_parsed'].explode().value_counts().head(10)
print("\n--- Top 10 Movie Genres ---")
print(genre_counts)

# Analyze movies per year
movies_per_year = movies_df['release_year'].value_counts().sort_index()
print("\n--- Movies Released Per Year (Sample) ---")
print(movies_per_year.head()) # print a sample for overview

print("\nData analysis completed!")


# --- 8. Data Visualization ---
print("\n--- Generating data visualizations ---")

# --- Chart 1: Movie Genre Distribution (Top 10) ---
plt.figure(figsize=(12, 6))
sns.barplot(x=genre_counts.index, y=genre_counts.values, palette='viridis')
plt.title('电影类型分布 (前10位)')
plt.xlabel('电影类型')
plt.ylabel('电影数量')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('movie_genres_distribution.png') # Save before showing
plt.show()
print("Chart 1: Movie Genre Distribution (Top 10) generated and saved!")


# --- Chart 2: Movie Profit Distribution (Positive Profits Only) ---
profitable_movies = movies_df[movies_df['profit'] > 0]
plt.figure(figsize=(12, 6))
sns.histplot(data=profitable_movies, x='profit', bins=50, kde=True, palette='viridis')
plt.title('电影利润分布 (只显示正利润电影)')
plt.xlabel('电影利润 (美元)')
plt.ylabel('电影数量')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
plt.tight_layout()
plt.savefig('movie_profit_distribution.png') # Save before showing
plt.show()
print("Chart 2: Movie Profit Distribution (Positive Profits Only) generated and saved!")


# --- Chart 3: Annual Movie Release Trend ---
plt.figure(figsize=(15, 7))
sns.lineplot(x=movies_per_year.index, y=movies_per_year.values, marker='o', palette='viridis')
plt.title('电影数量年度趋势')
plt.xlabel('年份')
plt.ylabel('电影数量')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('movies_per_year_trend.png') # Save before showing
plt.show()
print("Chart 3: Annual Movie Release Trend generated and saved!")


# --- Chart 4: Movie Average Vote Distribution ---
plt.figure(figsize=(10, 6))
sns.histplot(movies_df['vote_average'], bins=20, kde=True, palette='viridis')
plt.title('电影平均评分分布')
plt.xlabel('平均评分')
plt.ylabel('电影数量')
plt.tight_layout()
plt.savefig('movie_avg_vote_distribution.png') # Save before showing
plt.show()
print("Chart 4: Movie Average Vote Distribution generated and saved!")


# --- Chart 5: Movie Popularity Distribution ---
plt.figure(figsize=(10, 6))
sns.histplot(movies_df['popularity'], bins=20, kde=True, palette='viridis')
plt.title('电影流行度分布')
plt.xlabel('流行度')
plt.ylabel('电影数量')
plt.tight_layout()
plt.savefig('movie_popularity_distribution.png') # Save before showing
plt.show()
print("Chart 5: Movie Popularity Distribution generated and saved!")


# --- Chart 6: Movie Vote Count Distribution ---
plt.figure(figsize=(10, 6))
sns.histplot(movies_df['vote_count'], bins=20, kde=True, palette='viridis')
plt.title('电影投票人数分布')
plt.xlabel('投票人数')
plt.ylabel('电影数量')
plt.tight_layout()
plt.savefig('movie_vote_count_distribution.png') # Save before showing
plt.show()
print("Chart 6: Movie Vote Count Distribution generated and saved!")


# --- Chart 7: Correlation Heatmap (Budget, Revenue, Vote Average, Popularity) ---
correlation_matrix = movies_df[['budget', 'revenue', 'vote_average', 'popularity']].corr()
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f") # Add fmt=".2f" for 2 decimal places
plt.title('电影预算、票房、评分和流行度之间的相关性')
plt.tight_layout()
plt.savefig('correlation_heatmap.png') # Save before showing
plt.show()
print("Chart 7: Correlation Heatmap generated and saved!")

# --- 9. Final Project Statement ---
print("\n--- Project Execution Completed ---")
# Personal Goal Statement (from previous version)
goal = "我的目标是在IT领域不断学习和成长，未来成为一名优秀的软件工程师或数据科学家。"
print(f"\n我的目标是：{goal}")
print("--- End of Project ---")