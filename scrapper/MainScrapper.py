import json
import os
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from multiprocessing import current_process
# from vars import result_links
from selenium import webdriver as wb
from selenium.webdriver.common.keys import Keys
from datetime import datetime
# from mailjet_rest import Client
from multiprocessing import Process
from django.conf import settings
import glob
import re
import random

DATA_DIR = settings.BASE_DIR / 'data'
LINK_TEXTS_FILE = DATA_DIR / 'input' / 'links.txt'
LOG_FILE = DATA_DIR / 'logs.txt'


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

    return reg_list[year], base_link


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
                return html
    except:
        return None


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
    def __init__(self, sem, year):
        self.sem = sem
        self.year = year

    def get_result_link(self):
        with open('data/inputs/result_links.json') as f:
            result_links = json.load(f)
        return result_links[self.year][self.sem]

    def get_output_dir(self):
        output_dir = os.path.join(DATA_DIR, 'output', self.year, self.sem)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return output_dir

    @staticmethod
    def save_json(json_data, file_name):
        with open(file_name, "w") as f:
            json.dump(json_data, f, indent=2)

    @staticmethod
    def result_download(base_link, reg, save=True):
        html = download_html_bs(base_link, reg)
        return html

    @staticmethod
    def save_file(data, file_name):
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(data)

    def batch_result_download(self, regs):
        base_link = self.get_result_link()
        output_dir = self.get_output_dir()
        for reg in regs:
            result = self.result_download(base_link=base_link, reg=reg)
            self.save_file(result, os.path.join(output_dir, f"{reg}.html"))

    def jsonify_data(self):
        output_dir = self.get_output_dir()
        files = list(glob.glob(os.path.join(output_dir, "*.html")))
        json_data = {}

        errors = []
        for file in files:
            try:
                with open(file, encoding='utf-8') as f:
                    html = f.read()
                json_data[file.replace('.html', '')] = to_json(html)
            except Exception as e:
                errors.append(f"{file}: {e}\n")
        with open(os.path.join(output_dir, 'errors.txt'), 'w') as f:
            f.writelines(errors)

    @staticmethod
    def process_stats(processes):
        sleep_time = 30
        while any(map(lambda x: x.is_alive(), processes)):
            time.sleep(sleep_time)

    def multiprocess_download(self, regs, n_process=4):
        batch_size = len(regs) // n_process
        process_list = []
        for i in range(n_process):
            process = Process(
                target=self.batch_result_download,
                args=(regs[i * batch_size: (i + 1) * batch_size],)
            )
            process_list.append(process)
            process_list[-1].start()
        self.process_stats(process_list)

    @staticmethod
    def check_new_entry(result_link):
        _html = urlopen(result_link).read()
        soup = bs(_html, features="html.parser")
        rows = soup.find('table', {"class": "style1"}).findAll('tr')
        _tr_texts = list(map(lambda x: re.sub(r'[;.,\s]\s*', '', x.text.lower()), rows))
        return {
            '_html': _html,
            '_tr_texts': _tr_texts
        }

    @classmethod
    def find_sem(cls, text):
        ctext = re.sub(r'[;.,"\s]\s*', '', text.lower())
        data = {
            "is_btech_result": 'btech' in ctext,
        }
        sem = re.findall(r'\d[(st|nd|rd|th)]', text)
        data['sem'] = f'sem{sem[0][0]}' if sem else None
        return data

    @staticmethod
    def get_result_links(chrome, link, tr_id):
        random_regs = [random.randint(10_000_000_000, 20_000_000_000)
                       for i in range(2)]
        chrome.get(link)
        tr_list = chrome.execute_script(
            """return document.querySelector('table[class="style1"]').querySelectorAll('tr')"""
        )
        new_tr = tr_list[tr_id]
        sem_data = Scrapper.find_sem(new_tr.text)

        new_tr.click()
        tr_link = chrome.current_url
        new_data = []
        for reg in random_regs:
            try:
                chrome.get(tr_link)

                # enter reg no. and submit
                reg_inp = chrome.find_element_by_id("ctl00_ContentPlaceHolder1_TextBox_RegNo")
                reg_inp.send_keys(reg)
                reg_inp.send_keys(Keys.ENTER)

                # if "New Official Website of Aryabhatta Knowledge University" in chrome.page_source:
                link_data = {
                    "sem": sem_data['sem'],
                    "is_btech_result": sem_data['is_btech_result'],
                    "form_link": tr_link,
                    "res_link": chrome.current_url,
                    "base_res_link": chrome.current_url.rstrip(str(reg))
                }
                new_data.append(link_data)
            except:
                print("ERROR: error while extracting link.")
        if new_data:
            return new_data[0]
