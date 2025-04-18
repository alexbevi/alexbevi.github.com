# _plugins/jekyll_series_plugin.rb
# Jekyll plugin for navigating blog series using a blockquote prompt-info wrapper
# Utilizes Jekyll::Cache API to speed up builds
# Configuration in _config.yml:
# series_nav:
#   my-slug:
#     title: "Display Title"
#     description: "This series covers the fundamentals of X, Y, and Z."
#     title_link: "/series-overview/{{ page.series }}/"
# Usage in post front matter:
#   series: my-slug
# Invoke in layout/post template:
#   {% series_nav %}

require 'jekyll/cache'
require 'liquid'

module Jekyll
  class SeriesGenerator < Generator
    safe true
    priority :low

    def generate(site)
      cache          = Jekyll::Cache.new("series_nav")
      series_config  = site.config['series_nav'] || {}

      series_map = cache.getset("series_map") do
        Jekyll.logger.info "SeriesNav:", "Calculating series map"
        build_series_map(site.posts.docs, series_config)
      end

      site.data['series_map'] = series_map
      Jekyll.logger.info "SeriesNav:", "Series map loaded: #{series_map.keys.size} series"
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
        sorted_posts = info['posts'].sort_by(&:date)
        sorted_posts.each_with_index do |post, idx|
          post.data['series_posts']       = sorted_posts
          post.data['series_title']       = info['title']
          post.data['series_description'] = info['description']
          post.data['series_title_link']  = info['title_link']
          post.data['series_index']       = idx + 1
        end
        info['posts'] = sorted_posts
      end

      map
    end
  end

  class SeriesNavTag < Liquid::Tag
    def render(context)
      site       = context.registers[:site]
      page       = context.registers[:page]
      data       = site.data.dig('series_map', page['series'].to_s.strip)
      return '' unless data && data['posts']

      posts      = data['posts']
      current    = posts.find { |p| p.url == page['url'] }
      return '' unless current

      # Render title_link if any Liquid present
      title      = data['title']
      raw_title  = title
      if data['title_link']
        link_template = Liquid::Template.parse(data['title_link'])
        rendered_link = link_template.render!(context.environments.first, registers: context.registers)
        raw_title = "<a href='#{rendered_link}'>#{title}</a>"
      end

      # Wrapper blockquote for prompt-info styling
      html = +"<blockquote class='prompt-tip mb-6'>\n"
      html << "  <strong>Series: #{raw_title}</strong>\n"

      # Render description with Liquid processing
      if data['description']
        desc_template = Liquid::Template.parse(data['description'])
        rendered_desc = desc_template.render!(context.environments.first, registers: context.registers)
        html << "  <p>#{rendered_desc}</p>\n"
      end

      # Unordered list of posts: only prev, current, next
      html << "  <ul>
"
      # determine prev and next
      posts = data['posts']
      idx = posts.index(current)
      prev_post = idx > 0 ? posts[idx - 1] : nil
      next_post = idx < posts.size - 1 ? posts[idx + 1] : nil
      if prev_post
        prev_name = prev_post.data['title'] || File.basename(prev_post.url)
        html << "    <li>← <a href='#{prev_post.url}'>#{prev_name}</a></li>
"
      end
      # current
      curr_name = current.data['title'] || File.basename(current.url)
      html << "    <li><strong>#{curr_name}</strong></li>
"
      if next_post
        next_name = next_post.data['title'] || File.basename(next_post.url)
        html << "    <li>→ <a href='#{next_post.url}'>#{next_name}</a></li>
"
      end
      html << "  </ul>
"
      # Summary paragraph of series position of series position
      current_index = current.data['series_index']
      total = posts.size
      html << "  <p>This article is ##{current_index} of #{total} in this series.</p>
"
      html << "</blockquote>\n"

      html
    rescue => e
      Jekyll.logger.error "SeriesNavTag:", "Error rendering nav: #{e.message}"
      ''
    end
  end
end

Liquid::Template.register_tag('series_nav', Jekyll::SeriesNavTag)
