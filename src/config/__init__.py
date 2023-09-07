import logging

import yaml

logger = logging.getLogger('root')


class Config:
    def __init__(self):
        self.data = None
        self.config_file = None
        self.all_testcase = {}
        self.names = []
        self.currents = []
        self.selected_items = []
        self.size = -1

    def update_item_enabled(self, names, enabled):
        for item in self.all_testcase:
            if item['name'] in names:
                item['enabled'] = enabled
        self.all_testcase = sorted(self.all_testcase, key=lambda x: x["index"])
        self.currents = [item for item in self.all_testcase if item['enabled']]
        self.size = len(self.currents)
        self.save_config()

    def update_selected_items(self, names):
        self.selected_items.clear()
        for item in self.all_testcase:
            if item['name'] in names:
                self.selected_items.append(item)

    def load_config(self):
        # 读取 YAML 文件
        try:
            with open(self.config_file, 'r', encoding='utf-8') as yaml_file:
                self.data = yaml.safe_load(yaml_file)
                if 'AllTestCase' in self.data.keys():
                    self.all_testcase = self.data['AllTestCase']
                    self.all_testcase = sorted(self.all_testcase, key=lambda x: x["index"])
                    self.names = [item['name'] for item in self.all_testcase]
                    self.currents = [item for item in self.all_testcase if item['enabled']]
                    self.size = len(self.currents)
        except FileNotFoundError as e:
            logger.error(e)

    def save_config(self):
        # 保存YAML文件
        try:
            with open(self.config_file, 'w', encoding='utf-8') as yaml_file:
                yaml.safe_dump(self.data, yaml_file, allow_unicode=True)
        except FileNotFoundError as e:
            logger.error(e)
