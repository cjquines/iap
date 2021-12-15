# frozen_string_literal: true

require "jekyll"

module Jekyll
  module CategoryPages
    class CategoryPageGenerator < Jekyll::Generator
      safe true
      priority :lowest

      def generate(site)
        event = site.collections["events"]
        # collect all distinct interests
        interests = event.docs.map { |doc| doc.data["interests"] } .flatten.uniq!
        # for each interest, make a page
        interests.each do |interest|
          docs = event.docs.select { |doc| doc.data["interests"].include?(interest) }
          site.pages << CategoryPage.new(site, interest, docs)
        end
      end
    end

    class CategoryPage < Jekyll::Page
      def initialize(site, interest, docs)
        @site = site
        @base = site.source
        @dir = "interests"
        @basename = Jekyll::Utils.slugify(interest)
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
