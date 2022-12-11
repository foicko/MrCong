import asyncio
import aiohttp
import aiofiles
import bs4
from urllib.request import getproxies
import time

# 延迟时间
delay_time = 5

# 异步获取网页内容，并且使用代理
async def Get_HtmlAsync(_url):
    try:
        if(_url == ''):
            return
        async with aiohttp.ClientSession() as session:
            await asyncio.sleep(delay_time)
            async with session.get(_url, proxy=getproxies()['https']) as resp:
                return await resp.text()
    except:
        print("getHtmlAsync Error")

# 通过BeautifulSoup获取网盘链接
async def Get_BS4(url):
    if(url == ''): 
        return 
    text = await Get_HtmlAsync(url)
    bsoup = bs4.BeautifulSoup(text, 'lxml')
    a_list = bsoup.find_all('a', class_='shortc-button')
    res = []
    for i in a_list:
        res.append(i.get('href'))
    return res

# 写入文件
async def Write2File(data_list, des_location):
    async with aiofiles.open(des_location, 'a+', encoding='utf-8') as f:
        for i in data_list:
                await f.write(i+'\n')

# 读取文件
async def Read_From_File(des_location):
    async with aiofiles.open(des_location, 'r', encoding='utf-8') as f:
        return await f.read()

# 完成第二步，读取Step1.txt,写入Step2.txt
async def Get_Url_Need2Play():
    All_Url_Tasks = []
    pages = await Read_From_File('Step1.txt')
    pages_list = pages.split('\n')
    for i in pages_list:
        All_Url_Tasks.append(Get_BS4(i))

    All_Urls = await asyncio.gather(*All_Url_Tasks)
    List2Write = []
    for i in All_Urls:
        if i :
            for j in i:
                List2Write.append(j)
    for i in List2Write:
        print(i)
    await Write2File(List2Write,'Step2.txt')

async def Get_One_Url(url):
    text = await Get_HtmlAsync(url)
    bsoup = bs4.BeautifulSoup(text,'lxml')
    aim = bsoup.find('a', class_='input popsok').get('href')
    return aim

# 完成第三步，获取最终的下载地址到Step3.txt中
async def Get_DownloadUrl():
    data = await Read_From_File('Step2.txt')
    steps = data.split('\n')
    Tasks = []
    for i in steps:
        if 'mediafire' in i:
            Tasks.append(Get_One_Url(i))
    All_hrefs = await asyncio.gather(*Tasks)
    await Write2File(All_hrefs, 'Step3.txt')  


# 将所有步骤合并
async def MrCong():
    await Get_Url_Need2Play()
    await Get_DownloadUrl()

asyncio.run(MrCong())