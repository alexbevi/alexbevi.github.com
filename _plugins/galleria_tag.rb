# Title: Galleria Tag for Jekyll
# Authors: Alex Bevilacqua
# Description: incorporate the Galleria gallery jquery plugin
#
# Adaption of "Photos tag for Jekyll" by Devin Weaver, and the derived
# "Gallery Tag for Jekyll" by Kevin Brown.
#
# Installation:
#
# {% galleria_includes %}
#
# This macro should be added to your `source/_includes/custom/head.html`
# in order to load the libraries needed by Galleria
#
# Usage:
#
# Example:
#
# {% galleria %}
# photo1.jpg
# /path/to/photos/photo2.jpg:title
# {% endgalleria %}
#
module Jekyll

  class PhotosUtil
    def initialize(context)
      @context = context
    end

    def path_for(filename)
      filename = filename.strip
      prefix = (@context.environments.first['site']['baseurl'] unless filename =~ /^(?:\/|http)/i) || ""
      "#{prefix}#{filename}"
    end
  end

  class GalleriaScriptIncludePatch < Liquid::Tag
    def render(context)
      return <<-eof
<script src="https://cdnjs.cloudflare.com/ajax/libs/galleria/1.5.7/galleria.min.js"></script>
<link href="//cdnjs.cloudflare.com/ajax/libs/galleria/1.5.7/themes/classic/galleria.classic.min.css" media="screen, projection" rel="stylesheet" type="text/css" />
<style>
  /* This rule is read by Galleria to define the gallery height: */
  .galleria{ width: 700px; height: 400px; background: #000 }
  .responsive-wrap iframe{ max-width: 100%;}
</style>
      eof
    end
  end

  class GalleriaTag < Liquid::Block
    def initialize(tag_name, markup, tokens)
      # No initializing needed
      super
    end

    def render(context)
      # Convert the entire content array into one large string
      lines = super
      # split the text by newlines
      lines = lines.split("\n")

      p = PhotosUtil.new(context)
      gallery = "<div class=\"galleria\" />"
      gallery << "<script>"
      gallery << "var imageData = ["
      lines.each_with_index do |line, i|
        next if line.empty?
        filename, title = line.split(":")
        title = (title.nil?) ? filename : title.strip
        gallery << "{ image: '#{p.path_for(filename)}', title: '#{title}' },"
      end
      gallery << "];"
      gallery << "  Galleria.loadTheme('https://cdnjs.cloudflare.com/ajax/libs/galleria/1.5.7/themes/classic/galleria.classic.min.js');"
      gallery << "  Galleria.configure({ initialTransition: 'fadeslide', transition: 'fadeslide', dataSource: imageData, preload: 5, lightbox: true });"
      gallery << "  Galleria.run('.galleria');"
      gallery << "</script>"
      gallery
    end
  end

end

Liquid::Template.register_tag('galleria_old', Jekyll::GalleriaTag)
Liquid::Template.register_tag('galleria_includes', Jekyll::GalleriaScriptIncludePatch)
