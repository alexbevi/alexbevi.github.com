# frozen_string_literal: true

require "date"
require "jekyll"
require "yaml"

module Jekyll
  module SinglePageDev
    module Helpers
      FRONT_MATTER = /\A---\s*\n(.*?)\n---\s*\n/m.freeze
      POST_BASENAME = /\A(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})-(?<slug>.+)\z/.freeze

      module_function

      def active?(site)
        site.config["single_page_dev"] == true
      end

      def repo_root(site)
        root = site.config["single_page_dev_repo_root"].to_s
        return if root.empty?

        File.expand_path(root)
      end

      def locate_post(site, post)
        root = repo_root(site)
        return unless root

        relative_dir = post.path.to_s
        pattern = File.join(root, "_posts", relative_dir, "#{post.date}-#{post.slug}.*")
        Dir.glob(pattern).sort.first
      end

      def front_matter_for(path)
        match = File.read(path).match(FRONT_MATTER)
        return {} unless match

        data = YAML.safe_load(match[1], permitted_classes: [Date, Time], aliases: true) || {}
        data.is_a?(Hash) ? data : {}
      rescue StandardError
        {}
      end

      def post_url_for(site, path)
        basename = File.basename(path, File.extname(path))
        match = basename.match(POST_BASENAME)
        return unless match

        data = front_matter_for(path)
        slug = (data["slug"] || match[:slug]).to_s
        Jekyll::URL.new(
          :template     => site.posts.url_template || site.config["permalink"],
          :placeholders => {
            "year"       => match[:year],
            "month"      => match[:month],
            "i_month"    => match[:month].to_i.to_s,
            "day"        => match[:day],
            "i_day"      => match[:day].to_i.to_s,
            "short_year" => match[:year][-2, 2],
            "title"      => slug,
            "slug"       => slug,
            "categories" => categories_for(data["categories"]),
            "output_ext" => ""
          },
          :permalink    => data["permalink"]
        ).to_s
      end

      def categories_for(value)
        categories = Array(value).flat_map { |item| item.to_s.split("/") }.reject(&:empty?)
        return if categories.empty?

        categories.map { |item| Jekyll::Utils.slugify(item) }.join("/")
      end
    end

    class PostUrl < Jekyll::Tags::PostUrl
      def render(context)
        site = context.registers[:site]
        return super unless Helpers.active?(site)

        super
      rescue Jekyll::Errors::PostURLError => error
        path = Helpers.locate_post(site, @post)
        raise error unless path

        url = Helpers.post_url_for(site, path)
        raise error unless url

        relative_url(url)
      end
    end
  end
end

Liquid::Template.register_tag("post_url", Jekyll::SinglePageDev::PostUrl)
