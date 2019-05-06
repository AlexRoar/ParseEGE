#  Copyright (c) 2019.
#  Dremov Aleksander
#  dremov.me@gmail.com

import requests
import re
import datetime
import json
import os
from tqdm import tqdm
from bs4 import BeautifulSoup
import urllib.request
import random
import string
import ssl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import six
from lxml import etree
import shutil

ssl._create_default_https_context = ssl._create_unverified_context


class Root:
    topics = []
    base = {}
    topicReferences = {}

    def __init__(self, workdir='ParseEGE/data/', service='inf-ege'):
        if len(workdir) > 0:
            if workdir[-1] != '/':
                workdir += '/'
        self.workdir = workdir
        self.service = service

    def generateTopics(self):
        catalog = 'https://' + self.service + '.sdamgia.ru/'
        response = requests.get(catalog)
        data = response.content.decode('utf8')

        topics_raw = [m.start() for m in re.finditer('/test\?theme=', data)]
        topics = [data[i + 12:i + 15] for i in topics_raw]

        out = {
            'updated': str(datetime.datetime.now()),
            'data': topics
        }
        old = {}
        try:
            previous = open(self.workdir + 'topics.json')
            old = json.load(previous)
            previous.close()
        except:
            pass
        old[self.service] = out

        self.topics = out['data']

        save = open(self.workdir + 'topics.json', 'w')
        json.dump(old, save, indent=4, sort_keys=True)
        save.close()

    def getTopics(self):
        if (self.topics == []):
            if not os.path.isfile(self.workdir + 'topics.json'):
                self.generateTopics()
            else:
                previous = open(self.workdir + 'topics.json')
                old = json.load(previous)
                previous.close()
                self.topics = old[self.service]['data']
        return self.topics

    def loadDB(self):
        previous = open(self.workdir + 'parsed.json')
        old = json.load(previous)
        previous.close()
        return old

    def parseTasks(self, extended=True, doNotLoadDB=True, saveInLoop=False):
        base = {
            'updated': str(datetime.datetime.now()),
            'data': {},
            'dataId': {}
        }
        topics = self.getTopics()

        old = {}
        if not doNotLoadDB:
            try:
                old = self.loadDB()
                base['data'] = old[self.service]['data']
                base['dataId'] = old[self.service]['dataId']
            except:
                pass

        for i in range(len(topics)):
            i = topics[i]
            try:
                containers = self.parseOneTopic(i, extended)
                if containers == []:
                    continue
                top_ref = self.topicReferences[i]
                if not top_ref in set(base['data'].keys()):
                    base['data'][top_ref] = []
                base['data'][top_ref] = containers + base['data'][top_ref]
                for container in containers:
                    base['dataId'][container['task_id']] = container
            except Exception as e:
                print(e)
                print("Error in topic No " + str(i))
                continue

            if saveInLoop:
                self.base = base
                old[self.service] = base
                save = open(self.workdir + 'parsed.json', 'w')
                json.dump(old, save)
                save.close()

        self.base = base
        old[self.service] = base
        save = open(self.workdir + 'parsed.json', 'w')
        json.dump(old, save)
        save.close()

    #         I decided to save results in loop because of tricky errors,
    #         which can ruin everything.
    #         PS: loop is too slow even without saving, so we can sacrifice a bit.

    def getTopicName(self, id):
        catalog = 'https://' + self.service + '.sdamgia.ru/test?theme=' + str(id)
        response = requests.get(catalog)
        data = response.content.decode('utf8')
        soup = BeautifulSoup(data, 'html.parser')
        return self.getTopicNameFromSoup(soup)

    def getTopicNameFromSoup(self, soup):
        return soup.find('div', attrs={'class': 'new_header'}).get_text()

    def getTopicReference(self, id):
        catalog = 'https://' + self.service + '.sdamgia.ru/test?theme=' + str(id)
        response = requests.get(catalog)
        data = response.content.decode('utf8')
        soup = BeautifulSoup(data, 'html.parser')
        return self.getTopicReferenceFromSoup(soup)

    def getTopicReferenceFromSoup(self, soup):
        tmp = soup.find('span', attrs={'class': 'prob_nums'}).get_text()
        return tmp[8:tmp.find("№")]

    def directParseQuestion(self, q_id, extended=True):
        catalog = 'https://' + self.service + '.sdamgia.ru/problem?print=true&id=' + str(q_id)
        response = requests.get(catalog)
        data = response.content.decode('utf8')
        soup = BeautifulSoup(data, 'html.parser')
        # body = soup.find('div', attrs={'class': 'prob_maindiv'})

        container = {}

        body = soup
        task_id = body.find('span', attrs={'class': 'prob_nums'}).a.get_text()
        container['task_id'] = task_id

        body = soup
        question = body.find('div', attrs={'class': 'pbody'})
        container['question'] = question.get_text()
        if extended:
            container['questionRaw'] = str(question)

        body = soup
        solution = body.find('div', attrs={'id': 'sol' + str(q_id)})
        container['solution'] = solution.get_text()
        if extended:
            container['solutionRaw'] = str(solution)

        body = soup
        try:
            answer = body.find('div', attrs={'id': 'ans_key'})
            answer = answer.find('div', attrs={'class': 'prob_answer'})
            answer = list(answer.findAll('div'))[-1]
        except:
            answer = solution
        container['answer'] = answer.get_text()
        if extended:
            try:
                body = soup
                source = body.find('div', attrs={'class': 'attr1'})
                container['source'] = source.get_text()
            except:
                container['source'] = ''

        container['parsed'] = str(datetime.datetime.now())

        return container

    def parseOneTopic(self, id, extended=True):
        catalog = 'https://' + self.service + '.sdamgia.ru/test?theme=' + str(id)
        response = requests.get(catalog)
        data = response.content.decode('utf8')
        soup = BeautifulSoup(data, 'html.parser')
        print('\n\tParse:' + str(id) + ' -> ' + self.getTopicName(id))
        i = id

        if not i in set(self.topicReferences.keys()):
            try:
                top_ref = str(self.getTopicReference(id))
            except:
                return []
                # Will end up here if topic does not have any task
                # ex: https://inf-ege.sdamgia.ru/test?theme=316
            self.topicReferences[i] = top_ref
        else:
            top_ref = self.topicReferences[i]

        tasks = list(soup.find_all('div', attrs={'class': 'prob_view'}))
        out = []
        for j in tqdm(range(len(tasks))):
            container = {}
            task = tasks[j].div.find('div', attrs={'class': 'prob_maindiv'})
            task_id = task.find('span', attrs={'class': 'prob_nums'}).a.get_text()
            # print(task_id)
            if extended:
                container = self.directParseQuestion(task_id, extended)
            else:
                try:
                    task = tasks[j]
                    question = task.find('div', attrs={'class': 'pbody'}).get_text()

                    task = tasks[j]
                    solution = task.find(id='sol' + str(task_id)).get_text()

                    task = tasks[j]
                    answer = task.find('div', attrs={'class': 'answer'}).get_text()
                    if (answer[:7] == 'Ответ: '):
                        answer = answer[7:]
                    container['task_id'] = task_id
                    container['question'] = question
                    container['solution'] = solution
                    container['answer'] = answer
                    container['parsed'] = str(datetime.datetime.now())
                except Exception as e:
                    container = self.directParseQuestion(task_id, extended)
            container['reference'] = top_ref
            out.append(container)
        return out

    def obtainImages(self):
        topics = self.getTopics()
        for i in range(len(topics)):
            i = topics[i]
            catalog = 'https://' + self.service + '.sdamgia.ru/test?theme=' + str(i)
            response = requests.get(catalog)
            data = response.content.decode('utf8')
            soup = BeautifulSoup(data, 'html.parser')
            print('\n\tObtaining IMG:' + str(i) + ' -> ' + self.getTopicName(i))
            tasks = list(soup.find_all('div', attrs={'class': 'prob_view'}))
            try:
                top_ref = str(self.getTopicReference(i))
            except:
                continue
            for j in tqdm(range(len(tasks))):
                task = tasks[j].div.find('div', attrs={'class': 'prob_maindiv'})
                task_id = task.find('span', attrs={'class': 'prob_nums'}).a.get_text()
                task = tasks[j]
                images = task.findAll('img')

                for image in images:
                    src = image['src']
                    if src.count('id=') != 0:
                        src = 'https://' + self.service + '.sdamgia.ru' + src

                    ext = os.path.splitext(src)[1]
                    if ext == '':
                        ext = '.png'
                    # print(ext,src,end='\n\n\n\n')

                    path = self.workdir.strip() + self.service.strip()
                    path = path.strip()
                    path = path.replace(u'\xa0', u'')
                    if not os.path.isdir(path):
                        os.mkdir(path)
                    path += '/img'
                    path = path.strip()
                    path = path.replace(u'\xa0', u'')
                    if not os.path.isdir(path):
                        os.mkdir(path)
                    path = path.strip()
                    path = path.replace(u'\xa0', u'')
                    path += '/' + str(top_ref).strip()
                    if not os.path.isdir(path):
                        os.mkdir(path)
                    path = path.strip()
                    path = path.replace(u'\xa0', u'')
                    path += '/' + str(task_id)
                    if not os.path.isdir(path):
                        os.makedirs(path)
                    path += '/image_' + self.id_generator(size=4) + ext
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                    urllib.request.install_opener(opener)
                    try:
                        try:
                            urllib.request.urlretrieve(src, path)
                        except:
                            if (src.count('https') == 0):
                                src = src.replace('http', 'https')
                            urllib.request.urlretrieve(src, path)
                    except Exception as e:
                        print('\nCannot download image: ' + str(task_id) + ' ' + src)
                        print(e)

    def obtainTables(self):
        topics = self.getTopics()
        path = self.workdir.strip() + self.service.strip() + '/tables'
        if not os.path.isdir(path):
            os.mkdir(path)
        for i in range(len(topics)):
            i = topics[i]
            catalog = 'https://' + self.service + '.sdamgia.ru/test?theme=' + str(i)
            response = requests.get(catalog)
            data = response.content.decode('utf8')
            soup = BeautifulSoup(data, 'html.parser')
            print('\n\tObtaining TABLES:' + str(i) + ' -> ' + self.getTopicName(i))
            tasks = list(soup.find_all('div', attrs={'class': 'prob_view'}))
            try:
                top_ref = str(self.getTopicReference(i))
            except:
                continue
            path = self.workdir.strip() + self.service.strip() + '/tables'
            path += '/' + str(top_ref).strip()
            if not os.path.isdir(path):
                os.mkdir(path)

            for j in tqdm(range(len(tasks))):
                task = tasks[j].div.find('div', attrs={'class': 'prob_maindiv'})
                task_id = task.find('span', attrs={'class': 'prob_nums'}).a.get_text()
                task = tasks[j]
                tables = task.findAll('table')

                for table in tables:
                    table = str(table)
                    parser = etree.HTML(table).find("body/table")
                    rows = iter(parser)
                    # headers = [col.text for col in next(rows)]
                    out = []
                    for row in rows:
                        values = [col.text for col in row]
                        out.append(values)
                    if out == []:
                        continue
                    columns = []
                    maxl = max([len(i) for i in out])

                    for i in range(len(out)):
                        out[i] = out[i] + [None] * (maxl - len(out[i]))

                    for i in range(maxl):
                        columns.append([])
                    for i in out:
                        for j in range(len(i)):
                            columns[j].append(i[j])
                    # print(columns)
                    df = pd.DataFrame()
                    for i in range(len(columns)):
                        try:
                            df[str(i)] = columns[i]
                        except:
                            print(columns)
                            print(out)
                            print(i)
                            return
                    ax = self.render_mpl_table(df, header_columns=0, col_width=2.0)
                    ax = ax.get_figure()

                    path = self.workdir.strip() + self.service.strip() + '/tables'
                    path = path.strip()
                    path = path.replace(u'\xa0', u'')
                    path += '/' + str(top_ref).strip()
                    path = path.strip()
                    path = path.replace(u'\xa0', u'')
                    path += '/' + str(task_id)
                    if not os.path.isdir(path):
                        os.makedirs(path)

                    path += '/table_' + self.id_generator(size=4) + '.png'
                    ax.savefig(path, pad_inches=0.01, dpi=300, bbox_inches='tight')
                    plt.close(ax)

    def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def render_mpl_table(self, data, col_width=3.0, row_height=0.625, font_size=14,
                         header_color='#FFFFFF', row_colors=['#f1f1f2', 'w'], edge_color='w',
                         bbox=[0, 0, 1, 1], header_columns=0,
                         ax=None, **kwargs):
        if ax is None:
            size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
            fig, ax = plt.subplots(figsize=size)
            ax.axis('off')

        mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

        mpl_table.auto_set_font_size(False)
        mpl_table.set_fontsize(font_size)

        for k, cell in six.iteritems(mpl_table._cells):
            cell.set_edgecolor(edge_color)
            if k[0] == 0 or k[1] < header_columns:
                cell.set_text_props(weight='bold', color='w')
                cell.set_facecolor(header_color)
            else:
                cell.set_facecolor(row_colors[k[0] % len(row_colors)])
        return ax

    def explode(self):
        path = self.workdir.strip() + self.service.strip() + '/exploded'
        if not os.path.isdir(path):
            os.mkdir(path)
        else:
            shutil.rmtree(path)
            os.mkdir(path)

        old = self.loadDB()
        old = old[self.service]['data']

        keys = list(old.keys())

        # print(keys)

        for i in tqdm(range(len(keys))):
            i = keys[i]
            tmp_path = path + '/' + i
            os.mkdir(tmp_path)
            tasks = old[i]
            exploded = {
                'updated': str(datetime.datetime.now()),
                'data': tasks,
                'taskEGENumber': i.strip()
            }
            writer = open(tmp_path + '/tasks.json', 'w')
            json.dump(exploded, writer, ensure_ascii=False, indent=4, sort_keys=True)
            writer.close()


class Getter:
    topics = []
    base = {}

    def __init__(self, workdir='ParseEGE/data/', service='inf-ege'):
        if len(workdir) > 0:
            if workdir[-1] != '/':
                workdir += '/'
        self.workdir = workdir
        self.service = service
        if os.path.isfile(self.workdir + 'topics.json'):
            previous = open(self.workdir + 'topics.json')
            old = json.load(previous)
            previous.close()
            self.topics = old[self.service]['data']

        if os.path.isfile(self.workdir + 'parsed.json'):
            previous = open(self.workdir + 'parsed.json')
            old = json.load(previous)
            previous.close()
            self.base = old[self.service]['data']
