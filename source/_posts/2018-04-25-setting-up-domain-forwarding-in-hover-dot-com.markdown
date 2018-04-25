---
layout: post
title: "Setting up domain forwarding in hover.com"
date: 2018-04-25 15:27:08 -0400
comments: true
categories: [general]
---

I've known for a long time that when you navigate to my domain directly at [alexbevi.com](http://alexbevi.com) that you would be redirected to a [Hover](https://www.hover.com) placeholder page.

I've meant to add a domain redirect for a long time but just never got around to it ... until now.

If you log into your Hover control console at `https://www.hover.com/control_panel/domain/<your domain>`, you can just add the forward from the *Mangage Forwards* section.

* Click **Create a Forward**
* Select from the dropdown list
* Enter the full url (http://...) you would like requests to your domain to go to
* Click **Save Forward**

After about 15 minutes this will be active and all requests to your domain will redirect to the url you've selected.

{% img center /images/alexbevi-forward.png %}
