---
layout: post
title: "Building a Better Blog Series Plugin for Jekyll with ChatGPT"
date: 2025-04-20 07:42:45 -0400
comments: true
categories: Ruby
tags: [blog, jekyll, ruby]
image: /images/ChatGPT Image Apr 20, 2025, 10_18_59 AM.png
---

# Building a Better Blog Series Plugin for Jekyll with ChatGPT

In writing my blog series, ["Let's Adventure! A Journey into Adventure Games (1980-1999)"](https://alexbevi.com/blog/2021/07/28/adventure-games-1980-1999/), I found myself wanting a better way to handle navigation between posts. The existing Jekyll plugins and tutorials I found (such as those from [DigitalDrummerJ](https://digitaldrummerj.me/blogging-on-github-part-13-creating-an-article-series/) and [TotalDebug](https://totaldebug.uk/posts/jekyll-post-series-links/)) provided some inspiration but didn't fully align with my use case.

Initially, I tried existing plugins, but they lacked flexibility. Specifically, I needed:

- Dynamic generation of navigation links based on the series' metadata.
- Simple and intuitive integration with Jekyll's existing templating system.
- Robust error handling and graceful fallback behaviors.
- Ability to configure multiple series easily, ideally through `_config.yml`
- Easy integration with Jekyll's [Cache API](https://jekyllrb.com/tutorials/cache-api/) to enhance build performance.

Leveraging my increasing comfort with AI for research and coding tasks, I turned to ChatGPT ([full conversation here](https://chatgpt.com/share/6803cb78-d18c-800e-bf7e-d4e61df2c47a)). The conversational approach allowed me to iteratively specify requirements and rapidly prototype the plugin logic.

> The finished plugin is available at [https://github.com/alexbevi/jekyll-series-navigation](https://github.com/alexbevi/jekyll-series-navigation)
{: .prompt-info }

### Efficiency of Iterating via Chat Interface

One of the clearest demonstrations of the value of this approach came when I encountered a cryptic error during partial rendering:

```
SeriesNavTag: Error rendering nav: Liquid error: wrong number of arguments (given 1, expected 2..3)
```

At first, it wasn’t obvious what was causing this. But by sharing the full stack trace in ChatGPT, it became clear that the issue stemmed from how the `replace` filter was being used in a Liquid template—specifically in a custom tag that was incorrectly passing a single argument.

ChatGPT helped narrow this down quickly by examining the stack trace and correlating it with the standard method signatures expected in Liquid’s `replace` filter. It then provided the correct syntax and helped walk through validating each part of the rendering process.

This kind of issue could have taken a long time to debug in isolation, especially because it wasn't immediately clear whether the root cause was in Liquid syntax, plugin logic, or content metadata. With ChatGPT’s contextual understanding and ability to parse Ruby backtraces, we were able to identify and fix the bug by adjusting the argument structure in the tag rendering logic.

Working through the chat interface provided distinct advantages:
- **Immediate Feedback**: Real-time suggestions and error spotting accelerated development cycles, significantly reducing the time spent debugging. For example, ChatGPT quickly pointed out syntax issues within my Ruby and Liquid templates, helping resolve bugs in seconds rather than minutes or hours.
- **Rapid Prototyping**: Instant iteration allowed for quick experiments and adjustments, enabling me to refine features continuously based on the evolving requirements. I could quickly test multiple approaches for handling metadata and caching, instantly iterating through alternative implementations.
- **Clear Explanations**: Complex problems, such as issues with Liquid template variable passing, were clearly explained, improving my understanding and leading to quicker resolutions. When struggling with cache implementations, ChatGPT clearly illustrated the caching mechanism, dramatically shortening the learning curve.

### Implementing the Jekyll Series Plugin

Below is the Ruby plugin code (`series_nav.rb`) that was created through this AI-assisted process:

```ruby
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
      include_markup = "{% raw %}{% include series_nav.html %}{% endraw %}"
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
```

The code isn't perfect, and I'm sure I could simplify/improve it further, but for a few hours of just messing around with a prompt I think this is pretty good.

### Using the Plugin in Your Jekyll Blog

Integrate the following [Liquid partial](https://liquidjs.com/tutorials/partials-and-layouts.html) (`_includes/series_nav.html`) in your layout or post to display navigation links:

```html
{% raw %}
{%- comment -%}
/_includes/series_nav.html

Expected page data:
  page.series_title          # String title of the series
  page.series_description    # String description (HTML-safe)
  page.series_title_link     # URL or Liquid tag to link the title
  page.series_posts          # Array of all posts in this series (sorted)
  page.series_index          # Integer index of current post
  page.series_prev           # Previous post object or nil
  page.series_next           # Next post object or nil
{%- endcomment -%}

<blockquote class="prompt-tip mb-6">
  <strong>Series:&nbsp;
    {%- if page.series_title_link -%}
      <a href="{{ page.series_title_link }}">{{ page.series_title }}</a>
    {%- else -%}
      {{ page.series_title }}
    {%- endif -%}
  </strong>

  {%- if page.series_description -%}
    <p>{{ page.series_description }}</p>
  {%- endif -%}

  <ul class="list-none space-y-1">
    {%- if page.series_prev -%}
      <li>← <a href="{{ page.series_prev.url }}">{{ page.series_prev.title }}</a></li>
    {%- endif -%}

    <li><strong>{{ page.title }}</strong></li>

    {%- if page.series_next -%}
      <li>→ <a href="{{ page.series_next.url }}">{{ page.series_next.title }}</a></li>
    {%- endif -%}
  </ul>

  <p>Article {{ page.series_index }} of {{ page.series_posts | size }} in this series.</p>
</blockquote>
{% endraw %}
```

Since my site uses the [Chirpy Jekyll Theme](https://github.com/cotes2020/jekyll-theme-chirpy) I wanted the series navigation to seamlessly integrate, however the partial can be adapted as needed to suit your blog's layout.

### Integration Steps:
1. Place the Ruby plugin file (`series_nav.rb`) in your Jekyll site's `_plugins` directory.
2. Add the Liquid partial (`series_nav.html`) to your site's `_includes` directory.
3. Include the plugin tag in your post or layout template with `{% raw %}{% series_nav %}{% endraw %}`.

Ultimately, the plugin significantly streamlined navigation within my blog series, enhancing both my writing workflow and the reader's experience. This journey underscored how AI tools can complement traditional software development, enabling faster iterations, performance optimizations, and more elegant solutions.

Feel free to adapt this solution to your own Jekyll blog!

