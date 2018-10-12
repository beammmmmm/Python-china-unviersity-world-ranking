# -*- coding:utf-8 -*-
"""
抓取大学信息，并使用D3.js进行动态可视化
"""

import pandas as pd
import csv
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import time
import re

start_time = time.time()	#计算程序运行时间

# 获取网页内容
def get_one_page(year):
	"""获取一页网页的数据"""
	try:
		headers = {
			'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3.359.181 Safari/537.36'
				}
		# 英文版
		# url = 'http://www.shanghairanking.com/ARWU%s.html' % (str(year))
		
		# 中文版
		url = 'http://www.zuihaodaxue.com/ARWU%s.html' % (str(year))
		response = requests.get(url,headers=headers)
		
		# 2009-2015用GBK，2016-2018用UTF-8
		if response.status_code == 200:
			return response.content
		return None
	except RequestException:
		print("爬取失败")

# 解析表格
def parse_one_page(html,i):
	"""解析表格"""
	tb = pd.read_html(html)[0]
	# 重新命名表格列，不需要的列用数字表示
	tb.columns = ['world rank','university',2,3,'score',5]
	# 删除后面不需要的评分列
	#tb.drop([2,3,5,6,7,8,9,10],axis=1,inplace=True)
	
	#rank列100名后是区间，需要唯一化，增加一列index作为排名
	tb['index_rank'] = tb.index
	tb['index_rank'] = tb['index_rank'].astype(int) + 1
	
	# 增加一列年份
	tb['year'] = i
	
	# read_html 没有爬取country，需定义函数单独爬取
	tb['country'] = get_country(html)
	
	# 测试表格没有问题
	# print(tb)
	
	return tb
	
	#print(tb.info())		#查看表格信息
	#print(tb.columns.values)		#查看列表名称

# 获取国家名称
def get_country(html):
	"""获取国家名称"""
	soup = BeautifulSoup(html,'lxml')
	countries = soup.select('td > a > img')
	lst = []
	for i in countries:
		src = i['src']
		pattern = re.compile('flag.*\/(.*?).png')
		country = re.findall(pattern,src)[0]
		lst.append(country)
	return lst

# 保存表格至csv
def save_csv(tb):
	"""保存表格至csv"""
	tb.to_csv(r'university.csv', mode='a', encoding='utf_8_sig', header=True, index=0)
	
	endtime = time.time() - start_time
	# print('程序运行了%.2f秒' %endtime)
	
def analysis():
	"""进行数据分析"""
	df = pd.read_csv('university.csv')
	# 包含港澳台
	# df = df.query("(country == 'China')|(country == 'China-hk')|(country == 'China-tw')|(country == 'China-HongKong')|(country == 'China-Taiwan')|(country == 'Taiwan,China')|(country == 'HongKong,China')")[['university','year','index']]
	
	# 只包含内地
	df = df.query("(country == 'China')")
	
	# 将index_rank列转换为整型
	df['index_rank'] = df['index_rank'].astype(int)
		
	df['index_rank_score'] = df['index_rank']

	# 美国
	# df = df.query("(country == 'UniterStates')|(country == 'USA')")
	
	# 求topn 名
	def topn(df):
		"""求topn 名"""
		top = df.sort_values(['year','index_rank'],ascending = True)
		return top[:20].reset_index()
	
	df = df.groupby(by = ['year']).apply(topn)
	
	# 更改列顺序
	df = df[['university','index_rank_score','index_rank','year']]
	# 重命名列
	df.rename(columns = {'university':'name','index_rank_score':'type',
						'index_rank':'value','year':'date'},inplace=True)
	
	# 输出结果
	df.to_csv('university_rangking.csv',mode='w',encoding='utf_8_sig',header=True,index=False)
	
def main(year):
	for i in range(2009,year):	# 抓取10年
		html = get_one_page(i)
		tb = parse_one_page(html,i)
		save_csv(tb)
		print(i,'年排名提取完成。')
		analysis()

# 单进程
if __name__ == '__main__':
	main(2019)
	
	
	
	
	
