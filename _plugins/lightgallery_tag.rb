# Title: LightGallery Tag for Jekyll
# Authors: Alex Bevilacqua <alex@alexbevi.com>
# Description: incorporate the LightGallery gallery jquery plugin
#
# Adaption of "Photos tag for Jekyll" by Devin Weaver, and the derived
# "Gallery Tag for Jekyll" by Kevin Brown.
#
# Installation:
#
# {% gallery_includes %}
#
# This macro should be added to the `<HEAD>` of your template(s)
# in order to load the libraries and stylesheets needed by LightGallery
#
# Usage:
#
# {% gallery %}
# photo1.jpg
# /path/to/photos/photo2.jpg
# {% endgallery %}
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

  class LightGalleryScriptIncludePatch < Liquid::Tag
    def render(context)
      # https://cdnjs.com/libraries/lightgallery
      return <<-eof
<script src="https://cdnjs.cloudflare.com/ajax/libs/lightgallery/2.7.1/lightgallery.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/lightgallery/2.7.1/plugins/zoom/lg-zoom.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/lightgallery/2.7.1/plugins/thumbnail/lg-thumbnail.min.js"></script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/lightgallery/2.7.1/css/lightgallery-bundle.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/lightgallery/2.7.1/css/lg-transitions.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/lightgallery/2.7.1/css/lg-zoom.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/lightgallery/2.7.1/css/lg-thumbnail.min.css" rel="stylesheet">

<style>
  .inline-gallery-container {
    width: 100%;

    // set 60% height
    height: 0;
    padding-bottom: 65%;
  }
</style>
      eof
    end
  end

  class LightGalleryInlineTag < Liquid::Block
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

      gallery = "<div id='inline-gallery-container' class='inline-gallery-container'></div>"
      gallery << "<script>"
      gallery << "const lgContainer = document.getElementById('inline-gallery-container');"
      gallery << "const inlineGallery = lightGallery(lgContainer, {"
      gallery << "    container: lgContainer, licenceKey: \"C2D2C2BD-16BC4564-A4EAE653-401CB884\","
      gallery << "    dynamic: true,"
      gallery << "    hash: false,"
      gallery << "    closable: false,"
      gallery << "    showMaximizeIcon: true,"
      gallery << "    appendSubHtmlTo: '.lg-item',"
      gallery << "    slideDelay: 100,"
      gallery << "    dynamicEl: [ "
      lines.each_with_index do |line, i|
        next if line.empty?
        filename, title = line.split(":")
        title = (title.nil?) ? filename : title.strip
        gallery << "{ src: '#{p.path_for(filename)}', thumb: '#{p.path_for(filename)}' },"
      end
      gallery << "], thumbWidth: 60, thumbHeight: \"40px\", thumbMargin: 4 });"
      gallery << "inlineGallery.openGallery();"

      gallery
    end
  end

  class LightGalleryStaticThumbnailTag < Liquid::Block
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

      gallery = "<div id='static-thumbnails'>"
      lines.each_with_index do |line, i|
        next if line.empty?
        filename, title = line.split(":")
        title = (title.nil?) ? filename : title.strip
        gallery << "<a data-sizes='(min-width: 40em) 80vw, 100vw' href='#{p.path_for(filename)}'><img src='#{p.path_for(filename)}'></a>"
      end
      gallery << "</div>"
      gallery << "<script>"
      gallery << "lightGallery(document.getElementById('static-thumbnails'), {"
      gallery << "  animateThumb: false, thumbWidth: '80px', thumbHeight: '80px'"
      gallery << "  zoomFromOrigin: false,"
      gallery << "  allowMediaOverlap: true,"
      gallery << "  toggleThumb: true,"
      gallery << "});"
      gallery << "</script>"

      gallery
    end
  end

end

Liquid::Template.register_tag('galleria', Jekyll::LightGalleryInlineTag)
Liquid::Template.register_tag('gallery_thumbs', Jekyll::LightGalleryStaticThumbnailTag)

Liquid::Template.register_tag('galleria_includes', Jekyll::LightGalleryScriptIncludePatch)