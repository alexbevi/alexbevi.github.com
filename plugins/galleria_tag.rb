module Jekyll

  class PhotosUtil
    def initialize(context)
      @context = context
    end

    def path_for(filename)
      filename = filename.strip
      prefix = (@context.environments.first['site']['photos_prefix'] unless filename =~ /^(?:\/|http)/i) || ""
      "#{prefix}#{filename}"
    end
  end

  class GalleriaScriptIncludePatch < Liquid::Tag
    def render(context)
      return <<-eof
<script src="//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.1/jquery.min.js" type="text/javascript"></script>
<script src="//cdnjs.cloudflare.com/ajax/libs/galleria/1.4.2/galleria.min.js" type="text/javascript"></script>
<script src="//cdnjs.cloudflare.com/ajax/libs/galleria/1.4.2/themes/classic/galleria.classic.min.js" type="text/javascript"></script>
<link href="//cdnjs.cloudflare.com/ajax/libs/galleria/1.4.2/themes/classic/galleria.classic.min.css" media="screen, projection" rel="stylesheet" type="text/css" />
<style>
  /* This rule is read by Galleria to define the gallery height: */
  #galleria{height:320px}
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
      gallery = "<div id=\"galleria\">"

      lines.each_with_index do |line, i|
        next if line.empty?
        filename, title = line.split(":")
        title = (title.nil?) ? "" : title.strip
        gallery << "<img src=\"#{p.path_for(filename)}\" data-title=\"#{title}\" />"
      end
      gallery << "</div>"
      gallery << "<script>"
      gallery << "  Galleria.configure('transition', 'fade');"
      gallery << "  Galleria.run('#galleria');"
      gallery << "</script>"
      gallery
    end
  end

end

Liquid::Template.register_tag('galleria', Jekyll::GalleriaTag)
Liquid::Template.register_tag('galleria_includes', Jekyll::GalleriaScriptIncludePatch)
