# config.ru (Rack 3)
# frozen_string_literal: true
require "rack"
require "rack/files"
require "rack/utils"

ROOT = File.expand_path("_site", __dir__)

class TryIndex
  def initialize(app, root:)
    @app   = app
    @root  = root
    @files = Rack::Files.new(@root)  # Rack 3 replacement for Rack::File
  end

  def call(env)
    path = Rack::Utils.unescape_path(env["PATH_INFO"])

    # Try exact file, then "path.html", then "path/index.html"
    candidates = [
      path,
      "#{path}.html",
      File.join(path, "index.html")
    ].uniq

    candidates.each do |rel|
      full = File.join(@root, rel)
      if File.file?(full)
        # Serve the matched file by rewriting PATH_INFO for Rack::Files
        new_env = env.merge("PATH_INFO" => rel)
        return @files.call(new_env)
      end
    end

    @app.call(env) # fallthrough 404
  end
end

app = Rack::Builder.new do
  use Rack::Deflater
  use TryIndex, root: ROOT

  run ->(_env) { [404, { "Content-Type" => "text/plain" }, ["Not Found"]] }
end

run app
