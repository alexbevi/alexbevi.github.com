# frozen_string_literal: true

source "https://rubygems.org"

gem "jekyll-theme-chirpy", "~> 7.6"

# If you want to use GitHub Pages, remove the "gem "jekyll"" above and
# uncomment the line below. To upgrade, run `bundle update github-pages`.
# gem "github-pages", group: :jekyll_plugins
# If you have any plugins, put them here!
group :jekyll_plugins do
  gem 'jekyll-gist'
  gem 'jekyll-last-modified-at'
end

group :test do
  gem "html-proofer", "~> 5"
end

# Windows and JRuby does not include zoneinfo files, so bundle the tzinfo-data gem
# and associated library.
platforms :windows, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

# Performance-booster for watching directories on Windows
gem "wdm", "~> 0.2.0", :platforms => [:windows]

group :development do
  gem "faraday-retry"
  gem "stringex"
  gem "puma"
  gem "foreman"
  gem "rack"
end

gem "liquid-c"
gem "csv"
gem "base64"
gem "bigdecimal"
gem "ostruct"
