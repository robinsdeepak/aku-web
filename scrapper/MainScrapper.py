import json
import os
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from multiprocessing import current_process
# from vars import result_links
from selenium import webdriver as wb
from datetime import datetime
from mailjet_rest import Client


def get_config(year, sem):
    out_dir = os.path.join('data', 'output', 'results', year, sem)
    # out_dir_pd = os.path.join('data', 'output', 'pd', year, sem)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    with open('data/inputs/reg_list.json') as f:
        reg_list = json.load(f)
        # bce_reg_list = [reg for reg in reg_list[year] if reg[5:8] == '126']

    with open('data/inputs/result_links.json') as f:
        result_links = json.load(f)
        base_link = result_links[year][sem]

    return reg_list[year], base_link, out_dir


def start_chrome(headless=True):
    """
    return driver object
    """
    if not headless:
        return wb.Chrome()
    options = wb.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')
    chrome = wb.Chrome(options=options)
    return chrome


def exit_chrome(chrome):
    try:
        chrome.quit()
    except:
        pass


def log_error(error, log_file):
    """
    Logs error to a file with time stamp
    :param error: error message.
    :param log_file: file to write the log.
    :return: None
    """
    if not os.path.exists(os.path.join(os.getcwd(), 'logs')):
        os.makedirs('logs')

    with open(os.path.join('logs', log_file), 'a') as f:
        # f.write(time.ctime() + "\n" + error + "\n")
        f.write(error)


def log_print(log_file, DEBUG, *args):
    log_error(" ".join(map(lambda x: str(x), args)) + "\n", log_file)
    if DEBUG: print(*args)


def _processes_stat(processes):
    """
    keep tracks of processes running in multiprocessing and
    hold the execution until the all the processes completes.
    :param processes: list of Process objects.
    :return: None
    """
    while True:
        ps = list(map(lambda x: x.is_alive(), processes))
        if not any(ps):
            break
        print(ps, end='\r')
        time.sleep(60)


def save_to_gcp_bucket(bucket_credentials, file_path):
    pass


def download_html(chrome, base_link, reg):
    # chrome
    try:
        i = 0
        while True:
            if i % 10 == 0:
                chrome.get(f"{base_link}{reg}")
            time.sleep(.1)
            source = chrome.page_source
            i += 1
            if "Aryabhatta Knowledge University" in source:
                break
        return chrome.page_source
    except Exception as e:
        return None


def download_html_bs(base_link, reg):
    # Request
    try:
        i = 0
        while True:
            req = urlopen(f"{base_link}{reg}")
            if i % 10 == 0:
                time.sleep(.1)
            i += 1
            if req.code == 200:
                html = req.read()
                break
        return html
    except:
        return None


def download_and_save_results(base_link, REGS, OUT_DIR, dump_json=False):
    process_name = current_process().name.lower()
    chrome = start_chrome()
    json_data = dict()
    for reg in REGS:
        # html = download_html_bs(base_link, reg)
        html = download_html(chrome, base_link, reg)
        if html:
            try:
                with open(os.path.join(OUT_DIR, f'{reg}.html'), 'w', encoding='utf-8') as f:
                    f.write(html)
                if dump_json:
                    data = to_json(html)
                    json_data[reg] = data
                    with open(os.path.join(OUT_DIR, f'_{process_name}_data.json'), 'w') as f:
                        json.dump(json_data, f, indent=2)
            except Exception as e:
                # invalid reg
                # print(f"Invalid Reg: {reg}! -- {e}")
                continue
    # chrome.quit()


def to_json(html):
    soup = bs(html, 'html.parser')

    # parse data
    tp = ['theory', 'practical']
    data = dict()
    data['name'] = soup.find_all('table')[4].find_all('span')[1].text
    for k in range(2):
        tr = soup.find_all('table')[k + 6].find_all('tr')
        th = list(map(lambda x: x.text.strip(), tr[0].find_all('th')))
        data[tp[k]] = {}
        for i in range(1, len(tr)):
            td = list(map(lambda x: x.text.strip(), tr[i].find_all('td')))
            data[tp[k]][td[0]] = {}
            for j in range(1, len(th)):
                data[tp[k]][td[0]][th[j]] = td[j]
    # all_sem_gpa
    gpas = soup.find(id="ctl00_ContentPlaceHolder1_GridView3").find_all('tr')[-1].find_all('td')
    gpas = list(map(lambda x: x.text, gpas))
    data["GPA"] = gpas

    return data


class Scrapper:
    def __init__(self, reg, sem, year):
        self.reg = reg
        self.sem = sem
        self.year = year
        self.html = None
        self.json_data = None

    def get_result_link(self):
        return 'link'

    @property
    def result(self, save=True):
        base_link = self.get_result_link()
        html = download_html_bs(base_link, self.reg)
        if save:
            self.html = html
        return self.html

    def batch_result_download(self):
        pass

    @property
    def jsonify(self):
        if self.html:
            data = to_json(self.html)
        else:
            data = to_json(self.result)
        self.json_data = data
        return self.json_data
