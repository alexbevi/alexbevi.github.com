---
layout: post
title: "MongoDB ORMs, ODMs, and Libraries"
date: 2022-11-02 06:28:40 -0400
comments: true
categories: MongoDB
tags: ["ruby", "rails", "mongodb", "orm", "odm", "cross-post"]
image:
  src: /images/mongodb-logo.png
  alt: MongoDB Logo
canonical_url: https://www.mongodb.com/developer/products/mongodb/mongodb-orms-odms-libraries/
---
<div class="note info">
<small><em>Cross posted from <a href="https://www.mongodb.com/developer/products/mongodb/mongodb-orms-odms-libraries/">MongoDB Developer Center</a></em></small>
</div>

Though developers have always been capable of manually writing complex queries to interact with a database, this approach can be tedious and error-prone. [Object-Relational Mappers](https://en.wikipedia.org/wiki/Object%E2%80%93relational_mapping) (or ORMs) improve the developer experience, as they accomplish multiple meaningful tasks:

* Facilitating interactions between the database and an application by abstracting away the need to write raw SQL or database query language.
* Managing serialization/deserialization of data to objects.
* Enforcement of schema.

So, while it’s true that MongoDB offers [Drivers](https://www.mongodb.com/docs/drivers/) with idiomatic APIs and helpers for most  programming languages, sometimes a higher level abstraction is desirable. Developers are used to interacting with data in a more declarative fashion (LINQ for C#, ActiveRecord for Ruby, etc.) and an ORM facilitates code maintainability and reuse by allowing developers to interact with data as objects.

MongoDB provides a number of ORM-like libraries, and our [community](https://www.mongodb.com/docs/drivers/community-supported-drivers/) and partners have as well! These are sometimes referred to as ODMs (Object Document Mappers), as MongoDB is not a relational database management system. However, they exist to solve the same problem as ORMs do and the terminology can be used interchangeably.

The following are some examples of the best MongoDB ORM or ODM libraries for a number of programming languages, including Ruby, Python, Java, Node.js, and PHP.

## Beanie

Beanie is an Asynchronous Python object-document mapper (ODM) for MongoDB, based on [Motor](https://www.mongodb.com/docs/drivers/motor/) (an asynchronous MongoDB driver) and [Pydantic](https://pydantic-docs.helpmanual.io/).

When using Beanie, each database collection has a corresponding document that is used to interact with that collection. In addition to retrieving data, Beanie allows you to add, update, and delete documents from the collection. Beanie saves you time by removing boilerplate code, and it helps you focus on the parts of your app that actually matter.

See the [Beanie documentation](https://beanie-odm.dev/) for more information.

## Doctrine

Doctrine is a PHP MongoDB ORM, even though it’s referred to as an ODM. This library provides PHP object mapping functionality and transparent persistence for PHP objects to MongoDB, as well as a mechanism to map embedded or referenced documents. It can also create references between PHP documents in different databases and work with GridFS buckets.

See the [Doctrine MongoDB ODM documentation](https://www.doctrine-project.org/projects/doctrine-mongodb-odm/en/latest/index.html) for more information.

## Mongoid

Most Ruby-based applications are built using the [Ruby on Rails](https://rubyonrails.org/) framework. As a result, Rails’ [Active Record](https://guides.rubyonrails.org/active_record_basics.html) implementation, conventions, CRUD API, and callback mechanisms are second nature to Ruby developers. So, as far as a MongoDB ORM for Ruby, the Mongoid ODM provides API parity wherever possible to ensure developers working with a Rails application and using MongoDB can do so using methods and mechanics they’re already familiar with.

See the [Mongoid documentation](https://www.mongodb.com/docs/mongoid/current/) for more information.

## Mongoose

If you’re seeking an ORM for NodeJS and MongoDB, look no further than Mongoose. This Node.js-based Object Data Modeling (ODM) library for MongoDB is akin to an Object Relational Mapper (ORM) such as [SQLAlchemy](https://www.sqlalchemy.org/). The problem that Mongoose aims to solve is allowing developers to enforce a specific schema at the application layer. In addition to enforcing a schema, Mongoose also offers a variety of hooks, model validation, and other features aimed at making it easier to work with MongoDB.

See the [Mongoose documentation](https://mongoosejs.com/) or [MongoDB & Mongoose: Compatibility and Comparison](https://www.mongodb.com/developer/languages/javascript/mongoose-versus-nodejs-driver/) for more information.

## MongoEngine

MongoEngine is a Python ORM for MongoDB. Branded as a Document-Object Mapper, it uses a simple declarative API, similar to the Django ORM.

It was first released in 2015 as an open-source project, and the current version is built on top of [PyMongo](https://www.mongodb.com/docs/drivers/pymongo/), the official Python Driver by MongoDB.

See the [MongoEngine documentation](http://mongoengine.org/) for more information.

## Prisma

Prisma is a [new kind of ORM](https://www.prisma.io/docs/concepts/overview/prisma-in-your-stack/is-prisma-an-orm) for Node.js and Typescript that fundamentally differs from traditional ORMs. With Prisma, you define your models in the declarative [Prisma schema](https://www.prisma.io/docs/concepts/components/prisma-schema), which serves as the single source of truth for your database schema and the models in your programming language. The Prisma Client will read and write data to your database in a type-safe manner, without the overhead of managing complex model instances. This makes the process of querying data a lot more natural as well as more predictable since Prisma Client always returns plain JavaScript objects.

Support for MongoDB was one of the most requested features since the initial release of the Prisma ORM, and was added in version 3.12.

See [Prisma & MongoDB](https://www.prisma.io/mongodb) for more information.

## Spring Data MongoDB

If you’re seeking a Java ORM for MongoDB, Spring Data for MongoDB is the most popular choice for Java developers. The [Spring Data](https://spring.io/projects/spring-data) project provides a familiar and consistent Spring-based programming model for new datastores while retaining store-specific features and capabilities.

Key functional areas of Spring Data MongoDB that Java developers will benefit from are a POJO centric model for interacting with a MongoDB DBCollection and easily writing a repository-style data access layer.

See the [Spring Data MongoDB documentation](https://spring.io/projects/spring-data-mongodb) or the [Spring Boot Integration with MongoDB Tutorial](https://www.mongodb.com/compatibility/spring-boot) for more information.

## Go Build Something Awesome!

Though not an exhaustive list of the available MongoDB ORM and ODM libraries available right now, the entries above should allow you to get started using MongoDB in your language of choice more naturally and efficiently.

If you’re looking for assistance or have any feedback don’t hesitate to engage on our [Community Forums](https://www.mongodb.com/community/forums/).