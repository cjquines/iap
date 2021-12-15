# frozen_string_literal: true

require "jekyll"

module Jekyll
  module CategoryPages
    class CategoryPageGenerator < Jekyll::Generator
      safe true
      priority :lowest

      def generate(site)
        categories = ["types", "interests", "sponsors"]
        event = site.collections["events"]
        home = site.pages.find { |page| page.name == 'index.md' }
        categories.each do |category|
          # collect distinct filters for this category
          items = event.docs.map { |doc| doc.data[category] } .flatten.uniq!.sort!
          # inject into home.html template
          # so e.g. interests = ["Academic", academic.html, ...]
          home.data[category] = []
          # make the actual page for each item
          items.each do |item|
            docs = event.docs.select { |doc| doc.data[category].include?(item) }
            page = CategoryPage.new(site, category, item, docs)
            site.pages << page
            home.data[category] << [item, page.relative_path]
          end
        end
      end
    end

    class CategoryPage < Jekyll::Page
      def initialize(site, category, item, docs)
        @site = site
        @base = site.source
        @dir = category
        @basename = Jekyll::Utils.slugify(item)
        @ext = ".html"
        @name = @basename + @ext
        @data = {}
        data.default_proc = proc do |_, key|
          site.frontmatter_defaults.find(relative_path, :categories, key)
        end
      end
    end
  end
end
