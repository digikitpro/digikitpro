#!/usr/bin/env python3
"""Build the entire DigiKitPro static site. Run: python3 tools/build.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import *
import pages_blog, pages_main, pages_product, pages_misc, pages_category, pages_season, pages_guides, pages_partner, pages_audit

pages_main.load_articles = pages_blog.load_articles # shared loader
pages_misc.load_articles = pages_blog.load_articles
pages_product.load_articles = pages_blog.load_articles
pages_category.load_articles = pages_blog.load_articles
pages_season.load_articles = pages_blog.load_articles
pages_guides.load_articles = pages_blog.load_articles
pages_audit.load_articles = pages_blog.load_articles

def main():
    pages_main.build_home()
    pages_main.build_thanks()  # post-signup delivery page (moved from the removed Brush Finder module)
    pages_main.build_products()
    pages_main.build_freebies()
    pages_main.build_bundles()
    pages_category.build_categories()
    pages_guides.build_guides()  # buyer-guide landing pages (before misc: sitemap + search index read them)
    pages_partner.build_partner()  # partner portal (before misc: sitemap reads it)
    pages_season.build_seasons()
    pages_product.build_product_pages()
    pages_blog.build_blog()
    pages_audit.build_audit()  # SEO audit browsable HTML at /seo-audit/ (from docs/seo-audit/*.md)
    pages_misc.build_misc()
    pages_misc.build_pinterest_feed()
    untagged = untagged_products()
    if untagged:
        print("\nNOTICE: %d product(s) are missing an entry in data/discovery.json and used safe"
              " defaults (they still build and still sell, but the Brush Finder cannot recommend"
              " them well until tagged):\n  - %s" % (len(untagged), "\n  - ".join(untagged)))
    print("\nBUILD COMPLETE")

if __name__ == "__main__":
    main()
