---
layout: post
title: "Hello Product Management"
date: 2022-07-04 11:44:20 -0400
comments: true
categories: [Personal]
tags: [mongodb, career]
image: /images/mongodb-logo.png
---

## Past

My [MongoDB Career Journey]({% post_url 2018-08-14-hello-mongodb %}) began almost 4 years ago, and I've enjoyed my time as a [Technical Services Engineer]({% post_url 2018-10-01-technical-services-engineering-at-mongodb %}) immensely. During my tenure as part of the organization I had the opportunity to work with a number of high profile clients on some extremely challenging scenarios. These gave me a chance to write about some interesting aspects of the product such as [FTDC internals]({% post_url 2020-01-26-what-is-mongodb-ftdc-aka-diagnostic-dot-data %}), [change stream resume performance]({% post_url 2022-02-16-performance-analysis-of-resuming-a-mongodb-change-stream %}), [the impact of retryable writes on the oplog]({% post_url 2021-08-23-the-impact-of-retryable-writes-on-the-mongodb-oplog %}) and [replica set priority takeover mechanics]({% post_url 2021-09-30-ensuring-replica-set-priority-takeover-success %}).

While I advanced from a TSE to a Senior TSE and finally a Lead TSE I had the opportunity to contribute back to the core server and related products by adding tickets to the backlog. These were predominantly identified via reproductions initiated as a result of a customer-facing issue, and gave me a great deal of personal satisfaction to report. For anyone interested in the types of issues we can help identify, among the [100+ product tickets I've opened](https://jira.mongodb.org/issues?filter=-2&jql=reporter%20%3D%20%22alex.bevilacqua%40mongodb.com%22) in this time some of the most interesting were:

* [SERVER-36870](https://jira.mongodb.org/browse/SERVER-36870): Replication fails if server date exceeds January 19th, 2038
* [SERVER-44617](https://jira.mongodb.org/browse/SERVER-44617): `$regexFind` crash when one of the capture group doesn't match the input but pattern matches
* [SERVER-44891](https://jira.mongodb.org/browse/SERVER-44891): `collStats` will fail if resulting BSON size > 16MB
* [SERVER-57851](https://jira.mongodb.org/browse/SERVER-57851): Optimize `usersInfo` calls from `mongos` to CSRS PRIMARY for Authz User Role resolution
* [SERVER-59754](https://jira.mongodb.org/browse/SERVER-59754): Incorrect logging of `queryHash`/`planCacheKey` for operations that share the same `$lookup` shape
* [SERVER-62310](https://jira.mongodb.org/browse/SERVER-62310): `collMod` command not sent to all shards for a sharded collection if no chunks have been received

If the type of digital detective work that goes into finding and reporting these types of issues is appealing to you then Technical Services is always on the lookout for new engineers ;) Have a look at the [available opportunities](https://grnh.se/dcd90aac1) in your region and tell them Alex sent you :)

## Present

As much as I've loved my time in Technical Services, as of July 5th my journey moves in a different direction as I step into a new role as _Product Manager, Developer Experience_ focusing on the Ruby Driver and Ruby Language Ecosystem.

First of all, what is a Product Manager? According to [Atlassian](https://www.atlassian.com/agile/product-management/product-manager), _a product manager is the person who identifies the customer need and the larger business objectives that a product or feature will fulfill, articulates what success looks like for a product, and rallies a team to turn that vision into a reality._

Since this isn't another engineering role I will be stepping out of my comfort zone, but feel I am extremely well positioned internally at MongoDB to be successful with a role that advocates for Ruby developers! Since joining the Technical Services team in 2018 I quickly began focusing on [MongoDB Drivers](https://www.mongodb.com/docs/drivers/) focused cases, especially the [MongoDB Ruby Driver](https://www.mongodb.com/docs/ruby-driver/current/) and the [Mongoid ODM](https://www.mongodb.com/docs/mongoid/master/).

I've been working as a Ruby developer for more than a decade at this point, both as a Software Engineer building commercial applications and as a [Technical Services Engineer](https://www.mongodb.com/blog/post/technical-services-engineering-at-mongo-db-meet-alex-bevilacqua) helping MongoDB customers address production issues within their solutions. Heck, I've even [written a book](https://www.packtpub.com/product/redmine-plugin-extension-and-development/9781783288748) covering plugin development for a [Ruby on Rails based project management suite](https://www.redmine.org/).

I fell in love with the language and found it adopted and incorporated a lot of the best practices, ideas and design patterns of other languages. My feelings towards the language and community somewhat echo what [Matz](https://en.wikipedia.org/wiki/Yukihiro_Matsumoto) (the author of the [Ruby language](https://www.ruby-lang.org/en/)) stated more succinctly in [_The Ruby Programming Language_](https://www.oreilly.com/library/view/the-ruby-programming/9780596516178/):

> _I knew many languages before I created Ruby, but I was never fully satisfied with them. They were uglier, tougher, more complex, or more simple than I expected. I wanted to create my own language that satisfied me, as a programmer. I knew a lot about the language’s target audience: myself. To my surprise, many programmers all over the world feel very much like I do. They feel happy when they discover and program in Ruby._
>
> _Throughout the development of the Ruby language, I’ve focused my energies on making programming faster and easier. All features in Ruby, including object-oriented features, are designed to work as ordinary programmers (e.g., me) expect them to work. Most programmers feel it is elegant, easy to use, and a pleasure to program._
> ...
> >Ruby is designed to make programmers happy._
{: .prompt-tip }

## Future

This new role really feels like the culmination of a much longer journey that began when I started getting my feet wet with [MongoDB in 2012]({% post_url 2012-08-29-install-latest-mongodb-in-ubuntu %}), learned about Ruby drivers for MongoDB and was actively [troubleshooting Mongoid issues as early as 2014]({% post_url 2014-06-23-troubleshooting-a-mongoid-connection-issue %}).

My love of Ruby and my love of MongoDB should help give me a leg up in this new role, however the real work now begins! My focus will be to help drive adoption of MongoDB within the Ruby developer community, though how I can move the needle here remains to be seen.

I plan on sharing a lot more as this journey continues and I welcome any feedback you may have along the way.