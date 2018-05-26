#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

from book_parser import Output
from book_tester import (
    ChapterTest,
    CodeListing,
    write_to_file
)
from update_source_repo import update_sources_for_chapter

os.environ['LC_ALL'] = 'en_GB.UTF-8'
os.environ['LANG'] = 'en_GB.UTF-8'
os.environ['LANGUAGE'] = 'en_GB.UTF-8'


class Chapter1Test(ChapterTest):
    chapter_name = 'chapter_01'

    def write_to_file(self, codelisting):
        # override write to file, in this chapter cwd is root tempdir
        print('writing to file', codelisting.filename)
        write_to_file(codelisting, os.path.join(self.tempdir))
        print('wrote', open(os.path.join(self.tempdir, codelisting.filename)).read())


    def test_listings_and_commands_and_output(self):
        update_sources_for_chapter(self.chapter_name, previous_chapter=None)
        self.parse_listings()
        # self.fail('\n'.join(f'{l.type}: {l}' for l in self.listings))

        # sanity checks
        self.assertEqual(type(self.listings[0]), CodeListing)
        # self.assertEqual(self.listings[1].skip, True)

        self.skip_with_check(6, 'Performing system checks...') # after runserver
        self.listings[8] = Output(str(self.listings[8]).replace('$', ''))

        # prep folder as it would be
        self.sourcetree.run_command('mkdir -p virtualenv/bin')
        self.sourcetree.run_command('mkdir -p virtualenv/lib')

        # make sure we do write bytecodes so the __pycache__ bit of the book works
        if 'PYTHONDONTWRITEBYTECODE' in os.environ:
            del os.environ['PYTHONDONTWRITEBYTECODE']

        while self.pos < len(self.listings):
            print(self.pos)
            self.recognise_listing_and_process_it()


        self.assert_all_listings_checked(self.listings)

        # manually add repo, we didn't do it at the beginning
        local_repo_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '../source/chapter_01/superlists'
        ))
        self.sourcetree.run_command(
            'git remote add repo "{}"'.format(local_repo_path)
        )
        self.sourcetree.run_command(
            'git fetch repo'
        )

        self.check_final_diff(ignore=[
            "SECRET_KEY",
            "Generated by 'django-admin startproject' using Django 1.11.",
        ])


if __name__ == '__main__':
    unittest.main()
