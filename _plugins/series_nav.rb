# _plugins/jekyll_series_plugin.rb
# Jekyll plugin for navigating blog series using a blockquote prompt-info wrapper
# Utilizes Jekyll::Cache for performance; pre-renders Liquid in metadata within the tag context
# Configuration in _config.yml:
# series_nav:
#   my-slug:
#     title: "Display Title"
#     description: "Overview with {{ site.title }}"
#     title_link: "/series/{{ page.series }}/"
# Usage in post front matter:
#   series: my-slug
# Invoke in your layout/post template:
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
        build_series_map(site.posts.docs, series_config)
      end

      site.data['series_map'] = series_map
      Jekyll.logger.info 'SeriesNav:', "Loaded series map (#{series_map.keys.size} series)"
    end

    private

    # Builds a map of slug => { title, description, title_link, posts }
    def build_series_map(posts, config)
      map = {}

      posts.each do |post|
        slug = post.data['series'].to_s.strip
        next if slug.empty?

        cfg        = config.fetch(slug, {})
        title      = cfg['title'] || slug
        raw_desc   = cfg['description'] || ''
        raw_link   = cfg['title_link']  || ''

        map[slug] ||= {
          'title'       => title,
          'description' => raw_desc,
          'title_link'  => raw_link,
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
          post.data['series_prev']        = idx > 0 ? sorted[idx - 1] : nil
          post.data['series_next']        = idx < sorted.size - 1 ? sorted[idx + 1] : nil
        end
        info['posts'] = sorted
      end

      map
    end
  end

  class SeriesNavTag < Liquid::Tag
    def render(context)
      page = context.registers[:page]
      return '' unless page['series_posts']&.any?

      # Pre-render Liquid in title_link and description using this tag's context
      page['series_title_link'] = safe_render(context, page['series_title_link'])
      page['series_description'] = safe_render(context, page['series_description'])

      # Render include partial for final HTML
      include_markup = "{% include series_nav.html %}"
      template       = ::Liquid::Template.parse(include_markup)
      template.render!(context.environments.first, registers: context.registers)
    rescue => e
      Jekyll.logger.error 'SeriesNavTag:', "Error rendering include: #{e.message}"
      ''
    end

    private

    # Render Liquid in a string using the tag's current environment and registers
    def safe_render(context, text)
      return '' if text.to_s.strip.empty?
      tmpl = ::Liquid::Template.parse(text)
      tmpl.render!(context.environments.first, registers: context.registers)
    rescue => e
      Jekyll.logger.warn 'SeriesNavTag:', "Liquid rendering failed: #{e.message}"
      text
    end
  end
end

Liquid::Template.register_tag('series_nav', Jekyll::SeriesNavTag)
