#!/usr/bin/env python3
"""Build the entire DigiKitPro static site. Run: python3 tools/build.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import *
import pages_blog, pages_main, pages_product, pages_misc, pages_category

pages_main.load_articles = pages_blog.load_articles # shared loader
pages_misc.load_articles = pages_blog.load_articles
pages_product.load_articles = pages_blog.load_articles
pages_category.load_articles = pages_blog.load_articles

def main():
    pages_main.build_home()
    pages_main.build_products()
    pages_main.build_freebies()
    pages_main.build_bundles()
    pages_category.build_categories()
    pages_product.build_product_pages()
    pages_blog.build_blog()
    pages_misc.build_misc()
    print("\nBUILD COMPLETE")

if __name__ == "__main__":
    main()
