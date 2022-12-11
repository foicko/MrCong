import asyncio
import aiohttp
import aiofiles
import bs4
from urllib.request import getproxies
import time

# 延迟时间
delay_time = 3
# 加上这个可以解决443问题，大概是应用了Windows平台的策略，但是该策略限制了文件并发数，大约为500
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# 信号量机制，限制并发量
sem = asyncio.Semaphore(64)
# 异步获取网页内容，并且使用代理


async def Get_HtmlAsync(_url):
    try:
        if (_url == ''):
            return
        if _url:
            async with sem:
                async with aiohttp.ClientSession() as session:
                    async with session.get(_url, proxy=getproxies()['http']) as resp:
                        await asyncio.sleep(delay_time)
                        return await resp.text()
    except:
        print("getHtmlAsync Error")
    return

# 通过BeautifulSoup获取网盘链接


async def Get_BS4(url):
    if (url == ''):
        return
    if url:
        text = await Get_HtmlAsync(url)
        if text:
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
            if i:
                await f.write(i+'\n')

# 读取文件


async def Read_From_File(des_location):
    async with aiofiles.open(des_location, 'r', encoding='utf-8') as f:
        return await f.read()

# 获取


async def getOne_PageUrls(url):
    if url:
        text = await Get_HtmlAsync(url)
        if text:
            bsoup = bs4.BeautifulSoup(text, 'lxml')
            divs = bsoup.find_all('div', class_='post-thumbnail')
            urls = []
            for div in divs:
                urls.append(div.a.get('href'))
            return urls


# https://mrcong.com/page/105/
# 获取页面
async def GetAll_pageUrls(beg, end):
    base_url = 'https://mrcong.com'
    Tasks = []
    for i in range(beg, end+1):
        if i == 1:
            url = base_url
        else:
            url = base_url+'/page/'+str(i)
        print(url)
        Tasks.append(getOne_PageUrls(url))
    AllUrls = []
    ListOfList = await asyncio.gather(*Tasks)
    for list in ListOfList:
        if list:
            for i in list:
                if i:
                    AllUrls.append(i)
    existUrl = await Read_From_File('Step1.txt')
    exist_urlset = set(existUrl.split('\n'))
    All_urlset = set(AllUrls)
    diff = All_urlset.difference(exist_urlset)
    await Write2File(diff, 'Step1.txt')
    return diff


# 完成第二步，写入Step2.txt
async def Get_Url_Need2Play(diffSet):
    All_Url_Tasks = []
    # page = await Read_From_File('Step1.txt')
    pages_list = diffSet
    for i in pages_list:
        All_Url_Tasks.append(Get_BS4(i))
    All_Urls = await asyncio.gather(*All_Url_Tasks)
    List2Write = []
    for i in All_Urls:
        if i:
            for j in i:
                List2Write.append(j)
    await Write2File(List2Write, 'Step2.txt')
    return List2Write


async def Get_One_Url(url):
    try:
        text = await Get_HtmlAsync(url)
        if text:
            bsoup = bs4.BeautifulSoup(text, 'lxml')
            aim = bsoup.find('a', class_='input popsok').get('href')
            return aim
    except:
        await asyncio.sleep(2)
        print('Error')

# 完成第三步，获取最终的下载地址到Step3.txt中


async def Get_DownloadUrl(listtoSave):
    steps = listtoSave
    Tasks = []
    for i in steps:
        if 'mediafire' in i:
            Tasks.append(Get_One_Url(i))
    All_hrefs = await asyncio.gather(*Tasks)
    await Write2File(All_hrefs, 'Step3.txt')


# 将所有步骤合并
async def MrCong(beg, end):
    # diff = await GetAll_pageUrls(beg, end)
    # print('第一步完成')
    diff = (await Read_From_File('Step1.txt')).split('\n')[4000:]
    listtoSave = await Get_Url_Need2Play(diff)
    print('第二步完成')
    await Get_DownloadUrl(listtoSave)
    print('第三步完成')

# 增量更新功能

asyncio.run(MrCong(1, 2))
