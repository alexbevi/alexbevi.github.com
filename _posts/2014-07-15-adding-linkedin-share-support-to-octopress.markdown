---
layout: post
title: "Adding LinkedIn Share Support to Octopress"
date: 2014-07-15 15:55:14 -0400
comments: true
categories: [Ruby]
categories: [octopress]
---

I was looking for a plugin or an include to easily add [LinkedIn](http://www.linkedin.com/) support to the share options for my posts.

A quick Google search came up dry, so I figured I'd just roll my own.

<!--more-->

In order to accomplish this, all that is required is to edit `source/_includes/post/sharing.html`:

{% raw %}
```diff
diff --git a/source/_includes/post/sharing.html b/source/_includes/post/sharing.html
index e32500d..0bdd01e 100644
--- a/source/_includes/post/sharing.html
+++ b/source/_includes/post/sharing.html
@@ -5,6 +5,12 @@
   {% if site.google_plus_one %}
   <div class="g-plusone" data-size="{{ site.google_plus_one_size }}"></div>
   {% endif %}
+  {% if site.linkedin_share %}
+    <script src="//platform.linkedin.com/in.js" type="text/javascript">
+    lang: en_US
+  </script>
+  <script type="IN/Share" data-url="{{ site.url }}{{ page.url }}" data-counter="right"></script>
+  {% endif %}
   {% if site.facebook_like %}
     <div class="fb-like" data-send="true" data-width="450" data-show-faces="false"></div>
   {% endif %}
```
{% endraw %}

The change above adds a snippit of Javascript that passes the current `site.url` and `page.url` in a similar fashion as is done for Twitter.

The Javascript source was generated using LinkedIn's [Share Plugin Generator](https://developer.linkedin.com/plugins/share-plugin-generator), so if the format of the one I've chosen isn't to your liking, you can generate another.

Just in case you want to easily toggle this functionality, I've also set it up to check for a configuration value in your site's `_config.yml`:

```diff
diff --git a/_config.yml b/_config.yml
index f8f825c..2dce55b 100644
--- a/_config.yml
+++ b/_config.yml
@@ -104,4 +104,7 @@ google_analytics_tracking_id: xxx
 # Facebook Like
 facebook_like: true

+# LinkedIn Share
+linkedin_share: true
```

Now, the next time your site is regenerated, a LinkedIn share button will be available.

This same method could be used to add pretty much any other social sharing sites you may want, as most should provide some form of widget generator.