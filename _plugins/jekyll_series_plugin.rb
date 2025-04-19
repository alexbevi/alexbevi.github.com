# _plugins/jekyll_series_plugin.rb
# Jekyll plugin for managing blog series navigation
# Uses Jekyll::Cache API, and renders via a Liquid include (_includes/series_nav.html)
# Configuration in _config.yml:
# series_nav:
#   my-slug:
#     title: "Display Title"
#     description: "Overview of this series."
#     title_link: "/series/{{ page.series }}/"
# Usage in post front matter:
#   series: my-slug
# Invoke in your layout:
#   {% series_nav %}

require 'jekyll'
require 'jekyll/cache'
require 'liquid'

module Jekyll
  class SeriesGenerator < Generator
    safe true
    priority :low

    def generate(site)
      cache         = Jekyll::Cache.new('series_nav')
      series_config = site.config['series_nav'] || {}

      series_map = cache.getset('series_map') do
        Jekyll.logger.info 'SeriesNav:', "Building series map for #{site.posts.docs.size} posts"
        build_series_map(site.posts.docs, series_config)
      end

      site.data['series_map'] = series_map
      Jekyll.logger.info 'SeriesNav:', "Loaded series map (#{series_map.keys.size} series)"
    end

    private

    def build_series_map(posts, config)
      map = {}
      posts.each do |post|
        slug = post.data['series'].to_s.strip
        next if slug.empty?

        cfg         = config.fetch(slug, {})
        title       = cfg['title'] || slug
        description = cfg['description']
        title_link  = cfg['title_link']

        map[slug] ||= {
          'title'       => title,
          'description' => description,
          'title_link'  => title_link,
          'posts'       => []
        }
        map[slug]['posts'] << post
      end

      map.each do |slug, info|
        sorted = info['posts'].sort_by(&:date)
        sorted.each_with_index do |post, idx|
          post.data['series_posts']       = sorted
          post.data['series_title']       = info['title']
          post.data['series_description'] = info['description']
          post.data['series_title_link']  = info['title_link']
          post.data['series_index']       = idx + 1
          # store prev/next for direct access in template
          post.data['series_prev']        = (idx > 0 ? sorted[idx - 1] : nil)
          post.data['series_next']        = (idx < sorted.size - 1 ? sorted[idx + 1] : nil)
        end
        info['posts'] = sorted
      end

      map
    end
  end

  class SeriesNavTag < Liquid::Tag
    def render(context)
      page = context.registers[:page]
      # Only include if series data available
      return '' unless page['series_posts'] && page['series_posts'].any?

      # Render via include; relies on page.data fields set by generator
      include_markup = "{% include series_nav.html %}"
      template = Liquid::Template.parse(include_markup)
      # Render using current context (ensures page and site vars are available)
      template.render!(context.environments.first, registers: context.registers)
    rescue => e
      Jekyll.logger.error 'SeriesNavTag:', "Error rendering include: #{e.message}"
      ''
    end
  end
end

Liquid::Template.register_tag('series_nav', Jekyll::SeriesNavTag)
