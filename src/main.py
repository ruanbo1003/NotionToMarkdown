
import os
import requests
from notion_client import Client
from util import FileUtil

NOTION_TOKEN = "secret_key"
PAGE_IDS = [
    # "8d5eee980f264dd28a6c07e8ecabbb3c",
    "788d6c18679d4c4b9509b9db74f7fa28",
]
EXPORT_FOLDER = "./export"


class OnePageToMd(object):
    def __init__(self, folder, page_title, page_id):
        self.client = Client(auth=NOTION_TOKEN)
        self.folder = folder
        self.page_title = page_title
        self.page_id = page_id
        self.blocks = []
        self.img_count = 0
        self.numbered_list_index = 0

        self.child_level = 0
        self.md = ""

    def get_page_blocks(self):
        self.blocks = self.client.blocks.children.list(block_id=self.page_id, page_size=100)

    def download_image(self, img_url):
        response = requests.get(img_url)
        image_name = f"{self.folder}/{self.page_title}/image_{self.img_count}{FileUtil.get_image_format(img_url)}"

        file = open(image_name, "wb")
        file.write(response.content)
        file.close()

        return f"{self.page_title}/image_{self.img_count}{FileUtil.get_image_format(img_url)}"

    def pre_run(self):
        img_folder = os.path.join(self.folder, self.page_title)
        FileUtil.create_dir(img_folder)

    def post_run(self):
        if self.img_count == 0:
            img_folder = os.path.join(self.folder, self.page_title)
            FileUtil.delete_dir(img_folder)

    def get_block_data_and_convert(self, block_id, child_level):
        blocks = self.client.blocks.children.list(block_id=block_id, page_size=256)
        for each_block in blocks['results']:
            self.convert_one_block(each_block, child_level)

    def convert(self):
        self.pre_run()

        self.get_page_blocks()

        for each_block in self.blocks['results']:
            self.convert_one_block(each_block)

        md_name = os.path.join(self.folder, self.page_title + ".md")
        file = open(md_name, 'w')
        file.write(self.md)
        file.close()

        self.post_run()

    def append_to_md(self, item):
        self.md += item

    def convert_one_block(self, block, child_level=0):
        block_type = block['type']
        if block_type != 'numbered_list_item':
            self.numbered_list_index = 0

        block_data = "    " * child_level
        if block_type == 'paragraph':
            if block['paragraph']['rich_text']:
                text = block['paragraph']['rich_text'][0]['plain_text']
                if block['paragraph']['rich_text'][0]['href']:
                    block_data += f"[{text}]({block['paragraph']['rich_text'][0]['href']})"
                else:
                    block_data += text
        elif block_type == 'heading_1':
            block_data = "# " + block['heading_1']['rich_text'][0]['plain_text']
        elif block_type == 'heading_2':
            block_data = "## " + block['heading_2']['rich_text'][0]['plain_text']
        elif block_type == 'heading_3':
            block_data = "### " + block['heading_3']['rich_text'][0]['plain_text']
        elif block_type == 'numbered_list_item':
            self.numbered_list_index += 1
            block_data += str(self.numbered_list_index) + ". " + block['numbered_list_item']['rich_text'][0]['plain_text']
        elif block_type == 'bulleted_list_item':
            block_data += "- " + block['bulleted_list_item']['rich_text'][0]['plain_text']
        elif block_type == 'image':
            self.img_count += 1
            img_url = block['image']['file']['url']
            print(img_url)
            image_name = self.download_image(img_url)
            block_data += f"\n![]({image_name})"
        elif block_type == 'code':
            language = block['code']['language']
            code_text = ""
            if block['code']['rich_text']:
                code_text = block['code']['rich_text'][0]['plain_text']
            block_data = "\n```" + language + "\n" + code_text + "\n```"

        block_data = block_data.replace("\n", "\n" + "    " * child_level)
        block_data += "    " * child_level + "\n"

        self.append_to_md(block_data)

        if block['has_children']:
            next_block_id = block['id']
            self.get_block_data_and_convert(next_block_id, child_level + 1)


def test_sub_page_in_block():
    child_page_id = 'd5b26287-d718-4f03-b741-1b0b177a0fb4'
    to_md_util = OnePageToMd(EXPORT_FOLDER, "test", child_page_id)
    to_md_util.convert()


def main():
    FileUtil.create_dir(EXPORT_FOLDER)

    client = Client(auth=NOTION_TOKEN)
    for each_page_id in PAGE_IDS:
        # data = client.databases.retrieve(database_id=each_page_id)
        data = client.pages.retrieve(page_id=each_page_id)
        level_1_title = data['properties']['title']['title'][0]['plain_text']
        level_1_folder = os.path.join(EXPORT_FOLDER, level_1_title)
        FileUtil.create_dir(level_1_folder)

        page_children = client.blocks.children.list(block_id=each_page_id, page_size=1000)
        for each_child in page_children['results']:
            if each_child['object'] == 'block' and each_child['type'] == 'child_page':
                child_title = each_child['child_page']['title']
                child_page_id = each_child['id']
                to_md_util = OnePageToMd(level_1_folder, child_title, child_page_id)
                to_md_util.convert()

    client.close()


if __name__ == '__main__':
    main()

    # test_sub_page_in_block()
