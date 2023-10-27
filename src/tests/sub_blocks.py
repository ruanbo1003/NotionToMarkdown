
from ..main import OnePageToMd


def sub_pages_in_block():
    export_folder = "./export"
    child_page_id = 'd5b26287-d718-4f03-b741-1b0b177a0fb4'
    to_md_util = OnePageToMd(export_folder, "test", child_page_id)
    to_md_util.convert()


if __name__ == '__main__':
    sub_pages_in_block()
