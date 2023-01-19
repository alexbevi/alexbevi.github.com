---
layout: post
title: "Will Upgrading My MongoDB Server Version Break My Application?"
date: 2023-01-13 09:21:00 -0500
comments: true
categories: MongoDB
tags: [upgrade, drivers, mongodb]
image:
  src: /images/mongodb-logo.png
  alt: MongoDB Logo
---

Upgrading components is an important part of maintaining a healthy application. The MongoDB Server is continually being developed to include new features and functionality, as well as to fix bugs, potential vulnerabilities and attack vectors. To ensure users are using the "latest and greatest" whenever possible, MongoDB publicizes [Software Lifecycle Schedules](https://www.mongodb.com/support-policy/lifecycles) to make it clear when various components will reach end of life (EOL).

The applications that you've built that connect to MongoDB are using [MongoDB Drivers](https://www.mongodb.com/docs/drivers/), which at the time of writing include official releases for [C](https://www.mongodb.com/docs/drivers/c/), [C++](https://www.mongodb.com/docs/drivers/cxx/), [C# (.NET)](https://www.mongodb.com/docs/drivers/csharp/), [Go](https://www.mongodb.com/docs/drivers/go/current/), [Java](https://www.mongodb.com/docs/drivers/java-drivers/), [Node.js](https://www.mongodb.com/docs/drivers/node/current/), [PHP](https://www.mongodb.com/docs/drivers/php/), [Python](https://www.mongodb.com/docs/drivers/python/), [Ruby](https://www.mongodb.com/docs/ruby-driver/current/), [Rust](https://www.mongodb.com/docs/drivers/rust/), [Scala](https://www.mongodb.com/docs/drivers/scala/) and [Swift](https://www.mongodb.com/docs/drivers/swift/).

Note that "break my application" is extremely generic and is meant to encompass a category of issues such as "not being able to connect", "application can't start at all", "can't return data", etc.

## I'm using the Stable API!

The MongoDB [Stable API](https://www.mongodb.com/docs/manual/reference/stable-api/) was created to allow you to upgrade your MongoDB server at will, and ensure that behavior changes between MongoDB versions do not break your application.

The Stable API provides long-term API stability for applications and supports more frequent releases and automatic server upgrades. This allows your applications to take advantage of rapidly released features without risking backwards-breaking changes.

If your application is already using the Stable API via your current Driver you shouldn't have to worry further about compatibility as it relates to a MongoDB Server upgrade.

## What version of MongoDB does my Driver support?

Each official Driver listed above will contain a compatibility matrix (see the [Node.js Compatibility](https://www.mongodb.com/docs/drivers/node/current/compatibility/) as an example), which should clearly show you what MongoDB Server versions are actively being tested against which versions of the Driver.

![](/images/driver-compat-1.png)

<div class="note warning">
<small>Note that at the time of writing MongoDB <strong>does not</strong> have an official Support Policy for Drivers. If this changes in the future it would be reflected in the <a href="https://www.mongodb.com/changes-mongodb-support-policy">Changes to MongoDB Support Policy</a></small>
</div>

Neither the [Legacy Support Policy](https://www.mongodb.com/support-policy/legacy) nor the [Software Support Policy](https://www.mongodb.com/support-policy/software) call out drivers directly. As a result the best guidance to follow is to ensure the version of the MongoDB Driver your application is using is actively being tested against the version of the MongoDB Server you're using.

If you're using any [Community Supported Drivers](https://www.mongodb.com/docs/drivers/community-supported-drivers/), clarification regarding support and compatibility should be directed to those communities directly.

## What if I'm using a library that includes a MongoDB Driver?

Many popular [libraries, ORMs and ODMs]({% post_url 2022-11-02-mongodb-orms-odms-and-libraries %}) depend upon an official MongoDB Driver. Under most scenarios package management will be used to manage the library's dependencies, which can be used to determine which version of the MongoDB Driver is being used.

For example, let's consider some of the most popular libraries and ORMs. As the source code for most libraries are hosted on GitHub (or some other service) a similar strategy can be followed to identify what version of the MongoDB driver is being used for a given version of the library.

Many libraries use [Semantic Versioning](https://semver.org/), so if you're unsure how to determine if a given constraint (ex: `>=2.4.1', '<3.0.0'`) would include a version of a Driver (ex: `2.18.2`), the [Semver check](https://jubianchi.github.io/semver-check) tool can help.

### Mongoid

Mongoid is the ORM (or ODM) of choice for Ruby on Rails developers. As it is developed and maintained by MongoDB directly a [compatibility](https://www.mongodb.com/docs/mongoid/current/reference/compatibility/) page is available that can be used to identify what version of the library can be used with which versions of the MongoDB Server.

As a Ruby library however, dependencies are managed using [Bundler](https://bundler.io/), which implies either a `Gemfile` or `<library>.gemspec` will be present and should contain dependency and version details. Since the source code is available, if we wanted to identify what version of the Ruby Driver an older version of Mongoid (ex: `5.2.0`) required we could do the following:

1. Navigate to the [appropriate branch/tag on Github](https://github.com/mongodb/mongoid/tree/v5.2.0)
2. Open the [`mongoid.gemspec` file](https://github.com/mongodb/mongoid/blob/v5.2.0/mongoid.gemspec)
3. Identify what [versions of the driver are pinned](https://github.com/mongodb/mongoid/blob/v5.2.0/mongoid.gemspec#L31) (`"mongo", ['>=2.4.1', '<3.0.0']` in this case)

Note that your application's `Gemfile.lock` would indicate _exactly_ which version of the Driver is being used, however if you don't have access to this the above can help point you in the right direction.

### Mongoose

[Mongoose](https://mongoosejs.com/) provides a straight-forward, schema-based solution to model your Node.js application's data. It includes built-in type casting, validation, query building, business logic hooks and more, out of the box.

As a Node.js library, dependencies are managed using [Node Modules](https://nodejs.org/api/packages.html#modules-packages), which would indicate a `package.json` file would be present that describes the dependencies and version details. Since the source code is available, if we wanted to identify what version of the Node.js Driver an older version of Mongoose (ex: `4.9.9`) required we could do the following:

1. Navigate to the appropriate [branch/tag on Github](https://github.com/Automattic/mongoose/tree/4.9.9)
2. Open the [`package.json` file](https://github.com/Automattic/mongoose/blob/4.9.9/package.json)
3. Identify what [versions of the driver are pinned](https://github.com/Automattic/mongoose/blob/4.9.9/package.json#L26) (`"mongodb": "2.2.26"` in this case)

Note that your application's `package-lock.json` would indicate _exactly_ which version of the Driver is being used, however if you don't have access to this the above can help point you in the right direction.

### Spring Data MongoDB

[Spring Data MongoDB](https://spring.io/projects/spring-data-mongodb) is part of the umbrella Spring Data project which aims to provide a familiar and consistent Spring-based programming model for new datastores while retaining store-specific features and capabilities. The Spring Data MongoDB project provides integration with the MongoDB document database. Key functional areas of Spring Data MongoDB are a POJO centric model for interacting with a MongoDB DBCollection and easily writing a Repository style data access layer.

As a Java library, dependencies are managed using [Maven](https://maven.apache.org/index.html), which would indicate a `pom.xml` file would be present that describes the dependencies and version details. Since the source code is available, if we wanted to identify what version of the Node.js Driver an older version of Spring Data MongoDB (ex: `3.0.9.RELEASE`) required we could do the following:

1. Navigate to the [appropriate branch/tag on Github](https://github.com/spring-projects/spring-data-mongodb/tree/3.0.9.RELEASE)
2. Open the [`pom.xml` file](https://github.com/spring-projects/spring-data-mongodb/blob/3.0.9.RELEASE/pom.xml)
3. Identify what [versions of the driver are pinned](https://github.com/spring-projects/spring-data-mongodb/blob/3.0.9.RELEASE/pom.xml#L30) (`<mongo>4.0.6</mongo>` in this case, which is a variable referenced later to identify the appropriate driver version)\
  ```xml
    <dependency>
      <groupId>org.mongodb</groupId>
      <artifactId>mongodb-driver-core</artifactId>
      <version>${mongo}</version>
    </dependency>
  ```

## What if my version of the Driver isn't in the compatibility matrix?

The most important thing to understand about Driver versions when it comes to MongoDB is that **anything your current Driver was doing successfully while connected to MongoDB X.Y should _continue to work correctly_ while connected to a newer MongoDB Server**. This statement should be accurate if your upgrade path is taking you from a single [major release](https://www.mongodb.com/docs/manual/reference/versioning/) to the next highest release (ex: 5.0 to 6.0).

<div class="note info">
Backwards breaking changes that would prevent you from successfully connecting to a MongoDB Server from your current application occur <em>extremely rarely</em>. One example that is worth noting involves the <a href="https://www.mongodb.com/docs/manual/release-notes/5.1-compatibility/#std-label-legacy-op-codes-removed">removal of Legacy Opcodes</a> in MongoDB 6.0. If you have a version of a MongoDB Driver that predates the support for MongoDB 3.6 and the <a href="https://www.mongodb.com/docs/manual/reference/mongodb-wire-protocol/#op_msg"><tt>OP_MSG</tt></a> opcode, trying to interact with MongoDB 6.0+ Servers via these antiquated drivers will result in only errors being thrown due to unknown opcodes being used.
</div>

As a general rule of thumb, assuming the only change to your application stack is an upgraded MongoDB Server version:

* Your application _should_ continue to operate without issue
* You _should plan_ to upgrade to the latest driver to ensure you have the latest features and fixes
* You _should always_ test your MongoDB Server upgrades and application compatibility in a non-production environment **first** prior to upgrading your production environment and application(s)


