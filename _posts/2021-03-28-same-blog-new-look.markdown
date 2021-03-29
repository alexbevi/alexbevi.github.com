---
layout: post
title: "Same Blog, New Look!"
date: 2021-03-28 12:28:46 -0400
comments: true
categories: [Writing]
tags: [blog, jekyll, octopress]
---

Ever since I started this blog in 2012, I've been using [Octopress](http://octopress.org/) to generate the pages and push to generated content to [GitHub Pages](https://pages.github.com/) for hosting. Octopress is a set of scripts and helpers built on top of [Jekyll](https://jekyllrb.com/) and provided a lot of convenience in the form of deployment helpers, themes and scripts.

Unfortunately, Octopress fell out of maintenance many years ago (2015?) and has been stagnating ever since. As a number of Octopress users have before me, I decided it was time to migrate the site back to vanilla Jekyll. I also wanted to refresh the look and feel as version I had was beginning to feel ... dated:

![](/images/alexbevi-old.png)

I also wanted to continue managing the deployment client-side (as opposed to using automation via [GitHub Actions](https://github.com/features/actions)).

In the event this helps anyone, here's the process I followed.

### Migration

```bash
OLD_BLOG=/path/to/octopress/source

jekyll new blog
cd blog
bundle install

cp -R $OLD_BLOG/_posts/* _posts
cp -R $OLD_BLOG/images .

jekyll serve
```

Once copied over there will be some build failures when you try to run `jekyll serve`, such as:

* Missing plugins in `_plugins` directory (ex: can't render `{% img ... % }` tags)
* Missing plugins in `Gemfile`

Instead of hunting down an alternate plugin, for most of my build failures the issue was resolved by converting Liquid Tags versions of `img`, `blockquote`, and others to the pure Markdown versions instead.

### Look and Feel

I chose to use the [Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) theme for Jekyll as I like the dark look and navigation layout.

Following the installation and configuration steps was straightforward, however the one gotcha I hit was with [Jekyll Pagination](https://jekyllrb.com/docs/pagination/). Because I had both an `index.html` and `index.md` file in the blog root, the paginator wouldn't work until I deleted `index.md`.

### Deployment

Since I use GitHub Pages to host my site I wanted to be able to switch back and forth between old and new layouts while testing. I'm quite happy with the Octopress approach of deploying using `rake` tasks, so I just copied over parts of the existing `Rakefile` as follows:

```ruby
require "rubygems"
require "bundler/setup"
require "stringex"

posts_dir       = "_posts"    # directory for blog files
new_post_ext    = "markdown"  # default new post file extension when using the new_post task
deploy_dir      = "_site"     # deploy directory (for Github pages deployment)
deploy_branch  = "master2"

# usage rake new_post[my-new-post] or rake new_post['my new post'] or rake new_post (defaults to "new-post")
desc "Begin a new post in /#{posts_dir}"
task :new_post, :title do |t, args|
  if args.title
    title = args.title
  else
    title = get_stdin("Enter a title for your post: ")
  end
  filename = "#{posts_dir}/#{Time.now.strftime('%Y-%m-%d')}-#{title.to_url}.#{new_post_ext}"
  if File.exist?(filename)
    abort("rake aborted!") if ask("#{filename} already exists. Do you want to overwrite?", ['y', 'n']) == 'n'
  end
  puts "Creating new post: #{filename}"
  open(filename, 'w') do |post|
    post.puts "---"
    post.puts "layout: post"
    post.puts "title: \"#{title.gsub(/&/,'&amp;')}\""
    post.puts "date: #{Time.now.strftime('%Y-%m-%d %H:%M:%S %z')}"
    post.puts "comments: true"
    post.puts "categories: "
    post.puts "tags: "
    post.puts "---"
  end
end

desc "deploy public directory to github pages"
multitask :push do
  puts "## Deploying branch to Github Pages "
  puts "## Pulling any updates from Github Pages "
  cd "#{deploy_dir}" do
    Bundler.with_clean_env { system "git pull" }
  end
  cd "#{deploy_dir}" do
    system "git add -A"
    message = "Site updated at #{Time.now.utc}"
    puts "\n## Committing: #{message}"
    system "git commit -m \"#{message}\""
    puts "\n## Pushing generated #{deploy_dir} website"
    Bundler.with_clean_env { system "git push origin #{deploy_branch}" }
    puts "\n## Github Pages deploy complete"
  end
end

desc "Generate jekyll site"
task :generate do
  puts "## Generating Site with Jekyll"
  # system "compass compile --css-dir assets/css"
  system "jekyll build"
end

def get_stdin(message)
  print message
  STDIN.gets.chomp
end

def ask(message, valid_options)
  if valid_options
    answer = get_stdin("#{message} #{valid_options.to_s.gsub(/"/, '').gsub(/, /,'/')} ") while !valid_options.include?(answer)
  else
    answer = get_stdin(message)
  end
  answer
end
```

Since the `_site` directory where Jekyll generates content is in the `.gitignore`, we can initialize a new Git repo here:

```bash
cd _site
git init .
git remote add git@github.com:alexbevi/alexbevi.github.com.git
```

Once this is set up we can then build the site and publish it to a dedicated branch in our GitHub repository (I used `master2` in the above example):

```bash
rake generate
rake push
```

![](/images/alexbevi-gh1.png)

After changing the GitHub Pages source branch in our repository in GitHub, the blog was now using the new layout.

![](/images/alexbevi-site.png)
