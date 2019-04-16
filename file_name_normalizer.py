#!/usr/bin/env python3
"""
File name normalizer
(c) 2018 Takuma Watanabe <takumaw@sfo.kuramae.ne.jp>
"""

import os
import platform

import argparse
import unicodedata

class FileNameNormalizer:
    def has_special_characters(self, name):
        for c in name:
            try:
                unicodedata.name(c)
            except ValueError as e:
                return True
        return False

    def remove_special_characters(self, name):
        name_cleaned = []
        for c in name:
            try:
                unicodedata.name(c)
                name_cleaned.append(c)
            except ValueError as e:
                continue
        return "".join(name_cleaned)

    def replace_windows_illegal_characters(self, name):
        return name \
            .replace("<", "＜") \
            .replace(">", "＞") \
            .replace(":", "：") \
            .replace("\"", "”") \
            .replace("\\", "＼" )\
            .replace("/", "／") \
            .replace("|", "｜") \
            .replace("?", "？") \
            .replace("*", "＊") \
            .replace("~", "〜")

    def normalize(self, name, normalization_form="NFKC"):
        name_normalized = name
        name_normalized = unicodedata.normalize("NFKC", name_normalized)
        name_normalized = self.remove_special_characters(name_normalized)
        name_normalized = self.replace_windows_illegal_characters(name_normalized)
        return name_normalized

    def is_normalization_required(self, name, normalization_form="NFKC"):
        return name != self.normalize(name, normalization_form)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", action="append", nargs="+", help="a directory to scan", metavar="directory")
    parser.add_argument("-q", "--quiet", action="store_true", help="run quietly")
    parser.add_argument("--notest", action="store_true", help="actually do rename the files")
    args = parser.parse_args()

    file_name_normalizer = FileNameNormalizer()

    if platform.system() == "Darwin":
        normalization_form = "NFKD"
    else:
        normalization_form = "NFKC"

    for rootpath in args.directory[0]:
        while True:
            is_aborted = False
            for dirpath, dirnames, filenames in os.walk(rootpath):
                is_directory_structure_changed = False
                for name in filenames + dirnames:
                    if not file_name_normalizer.is_normalization_required(name, normalization_form):
                        continue

                    name_original = name
                    name_normarized = file_name_normalizer.normalize(name, normalization_form)
                    path_original = os.path.join(dirpath, name_original)
                    path_normalized = os.path.join(dirpath, name_normarized)

                    print(path_original)
                    print("->", path_normalized)
                    print("->", name_original.encode("utf-8"))
                    print("->", name_normarized.encode("utf-8"))

                    if os.path.exists(path_normalized):
                        print("->", "Target exists, skipping...")
                        continue

                    if os.path.isdir(path_original):
                        is_directory_structure_changed = True

                    if args.notest:
                        os.rename(path_original, path_normalized)

                if is_directory_structure_changed:
                    is_aborted = True
                    break
            if not is_aborted:
                break
