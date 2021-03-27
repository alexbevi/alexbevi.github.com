---
layout: post
title: "Redmine Knowledgebase 3.2.0 Released"
date: 2016-06-22 21:33:34 -0400
comments: true
categories: [redmine]
---

I haven't been very actively involved with this plugin or the Redmine community as a whole lately, but it would seem there is a very active user-base still logging bugs and enhancing this project.

You can grab a copy of the release [on GitHub](https://github.com/alexbevi/redmine_knowledgebase/releases/tag/v3.2.0).

I'm pushing out version 3.2.0 of the plugin thanks to the efforts of some very dedicated community members, who I'd like to highlight below:

Thanks to Frederico Camara:

* updating acts_as_rated to work with Redmine 3.2.x

Thanks to Eduard Kuleshov:

* getting this plugin supported in Redmine 3.0.x

Thanks to Axel Kämpfe:

* getting this plugin supported in Redmine 3.1.x and 3.2.x

HUGE thanks to Rob Spearman for basically taking over the project and pushing it forward:

## New Configuaration options

* Show articles without tabs
* Show attachments before article content
* Show thumbnails for articles in lists
* Show breadcrumbs for articles in lists

## New permissions

* Article history will only show up if have view permission
* optional permission for users to manage just their own articles. (#306)

## Layout

* Sort Tags on the index page
* Added authored view so users can find articles by author easily

<!-- more -->

## Bug Fixes

* article view counts not updating (#304)
* top rated list not valid (#305)
* ActiveRecord::StaleObjectError (Attempted to destroy a stale object: KbArticle) (#300)
* Error when generating a PDF of an article with pictures (#308)
* 500 Internal Server Error - if DELETE category but it's have subcategory (#293)

Note that this is a preliminary release as there is one bug in here that I haven't squashed.

When trying to search, you're prompted with a failure similar to:

```
Started GET "/search?utf8=%E2%9C%93&q=stuff" for 127.0.0.1 at 2016-06-23 01:14:06 +0000
Processing by SearchController#index as HTML
  Parameters: {"utf8"=>"✓", "q"=>"stuff"}
  Current user: admin (id=1)
Completed 500 Internal Server Error in 632ms (ActiveRecord: 173.6ms)

NoMethodError (undefined method `where' for #<Hash:0x000000096b0d60>):
  lib/plugins/acts_as_searchable/lib/acts_as_searchable.rb:93:in `search_result_ranks_and_ids'
  lib/redmine/search.rb:127:in `block in load_result_ids'
  lib/redmine/search.rb:125:in `each'
  lib/redmine/search.rb:125:in `load_result_ids'
  lib/redmine/search.rb:115:in `block in load_result_ids_from_cache'
  lib/redmine/search.rb:114:in `load_result_ids_from_cache'
  lib/redmine/search.rb:99:in `result_ids'
  lib/redmine/search.rb:70:in `result_count'
  app/controllers/search_controller.rb:65:in `index'
  lib/redmine/sudo_mode.rb:63:in `sudo_mode'
```

I'm pretty sure this has to do with how we're setting up `acts_as_searchable` in the `kb_article` model. Any suggestions welcome ;)
