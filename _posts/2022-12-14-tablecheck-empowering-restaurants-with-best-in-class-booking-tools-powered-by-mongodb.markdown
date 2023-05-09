---
layout: post
title: "TableCheck: Empowering Restaurants with Best-in-Class Booking Tools Powered by MongoDB"
date: 2022-12-14 14:49:43 -0500
comments: true
categories: "MongoDB"
tags: ["ruby", "rails", "mongodb", "orm", "odm", "customer-success", "cross-post"]
canonical_url: https://www.mongodb.com/developer/products/mongodb/customer-success-ruby-tablecheck/
image: /images/mongodb-logo.png
---

> Cross posted from the [MongoDB Developer Center](https://www.mongodb.com/developer/products/mongodb/customer-success-ruby-tablecheck/)
{: .prompt-info }

[TableCheck](https://tablecheck.com/) is the world’s premiere booking and guest platform. Headquartered in Tokyo, they empower restaurants with tools to elevate their guest experience and create guests for life with features like booking forms, surveys, marketing automation tools and an ecosystem of powerful solutions for restaurants to take their business forward.

## Architectural Overview of TableCheck

Launched in 2013, TableCheck began life as a [Ruby on Rails](https://rubyonrails.org/) monolith. Over time the solution has been expanded to include satellite microservices however one constant that has remained throughout this journey was MongoDB.

Originally TableCheck managed their own MongoDB Enterprise clusters, however once MongoDB Atlas became available they migrated their data to a managed replica set running in AWS.

According to CEO Johnny Shields, MongoDB was selected initially as the database of choice for TableCheck as it was _"love at first sight"_. Though MongoDB was a much different solution in 2013, even in the database product’s infancy it fit perfectly with their development workflow and allowed them to work with their data easily and quickly while building out their APIs and application.

## Ruby on Rails + MongoDB

Any developer familiar with Ruby on Rails knows that the [ORM](https://en.wikipedia.org/wiki/Object-relational_mapping) layer (via [Active Record](https://guides.rubyonrails.org/active_record_basics.html)) was designed to support relational databases. MongoDB’s [Mongoid ODM](https://www.mongodb.com/docs/mongoid/current/) acts as a veritable "drop-in" replacement for existing Active Record adapters so that MongoDB can be used seamlessly with Rails. The CRUD API is familiar to Ruby on Rails developers and makes working with MongoDB extremely easy.

When asked if MongoDB and Ruby were a good fit, Johnny Shields replied:
> _"Yes, I’d add the combo of MongoDB + Ruby + Rails + Mongoid is a match made in heaven. Particularly with the Mongoid ORM library, it is easy to get MongoDB data represented in native Ruby data structures, e.g. as nested arrays and objects"._

This has allowed TableCheck to ensure MongoDB remains the "golden-source" of data for the entire platform. They currently replicate a subset of data to Elasticsearch for deep multi-field search functionality, however given the rising popularity and utility of [Atlas Search](https://www.mongodb.com/docs/atlas/atlas-search/) this part of the stack may be further simplified.

As MongoDB data changes within the TableCheck platform, these changes are broadcast over [Apache Kafka](https://kafka.apache.org/) via the [MongoDB Kafka Connector](https://www.mongodb.com/docs/kafka-connector/current/) to enable downstream services to consume it. Several of their microservices are built in [Elixir](https://elixir-lang.org/), including a data analytics application. PostgreSQL is being used for these data analytics use cases as the only MongoDB Drivers for Elixir and managed by the community (such as [`elixir-mongo/mongodb`](https://github.com/elixir-mongo/mongodb) or [`zookzook/elixir-mongodb-driver`](https://github.com/zookzook/elixir-mongodb-driver)), however should an official Driver surface this decision may change.

## Benefits of the Mongoid ODM for Ruby on Rails Development

The "killer feature" for new users discovering Ruby on Rails is [Active Record Migrations](https://guides.rubyonrails.org/active_record_migrations.html). This feature of Active Record provides a DSL that enables developers to manage their relational database’s schema without having to write a single line of SQL. Because MongoDB is a NoSQL database, migrations and schema management are unnecessary!

Johnny Shields shares the following based on his experience working with MongoDB and Ruby on Rails:
> _"You can add or remove data fields without any need to migrate your database. This alone is a "killer-feature" reason to choose MongoDB. You do still need to consider database indexes however, but MongoDB Atlas has a profiler which will monitor for slow queries and auto-suggest if any index is needed."_

As the Mongoid ODM supports large portions of the Active Record API, another powerful productivity feature TableCheck was able to leverage is the use of [Associations](https://www.mongodb.com/docs/mongoid/current/reference/associations/). Cross-collection referenced associations are available, however unlike relational databases [embedded associations](https://www.mongodb.com/docs/mongoid/current/reference/associations/#embedded-associations) can be used to simplify the data model.

## Open Source and Community Strong

Both [`mongodb/mongoid`](https://github.com/mongodb/mongoid) and [`mongodb/mongo-ruby-driver`](https://github.com/mongodb/mongo-ruby-driver) are licensed under OSI approved licenses and MongoDB encourages the community to contribute feedback, issues and pull requests!

Since 2013, the TableCheck team has contributed nearly 150 PRs to both projects. The majority tend to be quality-of-life improvements and bug fixes related to edge-case combinations of various methods/options. They’ve also helped improve the accuracy of documentation in many places, and have even helped the MongoDB Ruby team setup Github Actions so that it would be easier for outsiders to contribute.

With so many contributions under their team’s belt, and clearly able to extend the Driver and ODM to fit any use case the MongoDB team may not have envisioned, when asked if there were any use-cases MongoDB couldn’t satisfy within a Ruby on Rails application the feedback was:
> _"I have not encountered any use case where I’ve felt SQL would be a fundamentally better solution than MongoDB. On the contrary, we have several microservices which we’ve started in SQL and are moving to MongoDB now wherever we can."_

The TableCheck team are vocal advocates for things like better changelogs, more discipline in following semantic versioning best practices. These have benefited the community greatly, and Johnny and team continue to advocate for things like adopting static code analysis (ex: via [Rubocop](https://github.com/rubocop/rubocop)) to improve overall code quality and consistency.

## Overall Thoughts on Working With MongoDB and Ruby on Rails

TableCheck has been a long-time user of MongoDB via the Ruby driver and Mongoid ODM, and as a result has experienced some growing pains as the data platform matured. When asked about any challenges his team faced working with MongoDB over the years Johnny replied:
> _"The biggest challenge was that in earlier MongoDB versions (3.x) there were a few random deadlock-type bugs in the server that bit us. These seemed to have gone away in newer versions (4.0+). MongoDB has clearly made an investment in core stability which we have benefitted from first-hand. Early on we were maintaining our own cluster, and from a few years ago we moved to Atlas and MongoDB now does much of the maintenance for us"._

We at MongoDB continue to be impressed by the scope and scale of the solutions our users and customers like TableCheck continue to build. Ruby on Rails continues to be a viable framework for enterprise and best-in-class applications, and our team will continue to grow the product to meet the needs of the next generation of Ruby application developers.

Johnny presented at [MongoDB Day Singapore](https://www.mongodb.com/events/mongodb-days-apac-2022/singapore) on November 23, 2022 ([view presentation](https://vimeo.com/780220683)). His talk covered a number of topics, including his experiences working with MongoDB and Ruby.