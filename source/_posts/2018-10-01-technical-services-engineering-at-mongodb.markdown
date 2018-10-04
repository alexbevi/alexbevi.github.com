---
layout: post
title: "Technical Services Engineering at MongoDB"
date: 2018-10-01 15:39:28 -0400
comments: true
categories: [mongodb]
---

The goal of this post is to provide a first hand account of what it means to be a *Technical Services Engineer* at [MongoDB](https://www.mongodb.com/careers/jobs/791258), as well as what the journey getting to this point has looked like for me.

### WHO AM I?

I have been working in Application Development and Software Engineering for nearly two decades. I started off writing desktop applications in VB6, then eventually in VB.NET, C++ and C#. When it was time to shift focus to web development I started off with HTML/JS/CSS (as we all do :P), then eventually Flash/AS3, Flex, Python, Ruby/Rails and Node.js.

I love solving problems programatically, and especially enjoy identifying opportunities for automation which can be addressed through custom tooling.

This led me down an informal DevOps track, as I was finding there was a need for optimization in the infrastructure layers that my applications were deployed to. This led me deeper into Linux internals, system administration and network operations.

While I was gaining these new skill-sets my primary focus was always on application development and delivery. Before coming to MongoDB I was working as a Development Lead / System Architect, but I found that my focus was always being drawn back to solving performance challenges at the infrastructure level.

<!-- MORE -->

### WHY MONOGODB?

I started working with MongoDB on a number of "hobby" projects around 2012. At the time I really only had experience with RDBMS', but due to the unstructured nature of the data I was working with decided to give this new technology a whirl.

I fell in love with the database almost immediately, and have since carried it forward to multiple new employers, as well as contract opportunities and consulting engagements.

The low barrier to entry from a development bootstrapping perspective made it the ideal backend for proof-of-concept development through to production deployment.

As a result of this increased activity with MongoDB, I found my self doing a lot more investigation into [performance issues](/blog/2018/05/28/troubleshooting-a-mongodb-performance-issue/) and [internals](/blog/2016/02/10/recovering-a-wiredtiger-collection-from-a-corrupt-mongodb-installation/) (links are to blog posts of challenges I encountered and resolved).

### WHY TECHNICAL SERVICES?

This was initially very challenging for me, as I had pre-conceived notions as to what "technical services" actually implied. The first thoughts that popped in my head were "technical support", "client support", "call center style support", etc.

While researching this position I came across a blog post from about six years ago by a MongoDB employee who blogged about his experience as a Support Engineer (in this [two](http://blog.markofu.com/2012/07/being-support-engineer-10gen-part-1.html) [part](http://blog.markofu.com/2012/10/being-support-engineer-10gen-part-2.html) series).

I found his reasons for joining MongoDB (10gen at the time), description of what kinds of challenges the job poses on a daily basis and how there is a constant push for self improvement and continuing education to align with what I was looking for in a new opportunity.

### WHAT'S A TECHNICAL SERVICES ENGINEER ON PAPER

To answer this question, let's start off by analyzing the [job posting](https://www.mongodb.com/careers/jobs/791258) that kicked off this journey for me in the first place.

{% img /images/why_tse/why_tse_001.png %}

So they're looking for people that are able to solve problems and communicate clearly. This could be a call center gig after all ... oh wait, *experts in MongoDB related database servers, drivers, tools, services* ... hrm, maybe there's a bit more to this.

{% img /images/why_tse/why_tse_002.png %}

*Architecture, performance, recovery, security*, those are a lot more complex than what you would face in a traditional support role. What really sold me though was the *contribute to internal projects* statement, as this aligned perfectly with my desire for process improvement through custom tooling.

{% img /images/why_tse/why_tse_003.png %}

By the time I got to this point in the job posting I was already sold. MongoDB is either trying to staff their first tier support with ridiculously over-qualified employees, or Technical Services really isn't what I would have thought.

I was sold. I proceeded to fill out the application, attach my resume and cover letter and crossed my fingers.

### WHAT'S A TECHNICAL SERVICES ENGINEER IN PRACTICE

After working with other TSEs for the past two months and having had an opportunity to handle some of my own cases I think I can shed a bit of light on what this role really entails.

#### HOW IS IT A SUPPORT ROLE?

A Technical Services Engineer interacts with MongoDB's clients via a support queue. This allows incoming "cases" to be prioritized and categorized to allow engineers to quickly identify what form of subject matter expertise may be required (ex: `Indexing`, `Replication`, `Sharding`, `Performance`, `Networking`, etc).

As a TSE you're responsible for claiming cases from a queue and providing feedback in a timely fashion that is clear, concise and technically accurate.

#### HOW IS IT AN ENGINEERING ROLE?

Here's the juicy part of this job. Although replying to client requests is the "deliverable" for a TSE, how you go about reproducing their issues requires a very deep understanding of MongoDB internals, software engineering, network engineering, infrastructure architecture and technical troubleshooting.

If a client is experiencing a performance related issue, you have an opportunity to replicate this behavior locally or in the cloud in any way you choose. You can write your own scripts, write your own tools, parse and analyze logs, consult with other TSEs, etc.

With each case you learn more about the inner working of the database, the tools, the drivers and OS level performance.

### CONCLUSION?

I'm leaving the closing section here as a question, as the TSE role continues to be redefined and refined as new MongoDB products come on board and new challenges present themselves.

What will likely remain constant though is the need for new engineers to have the following characteristics:

* a passion for continuing technical education
* a willingness to step outside their comfort zone
* an interest in software engineering
* an interest in network operations

I encourage you to check out the available [engineering](https://www.mongodb.com/careers/departments/engineering) jobs if what I've described here interests you (I swear HR is not putting me up to this ...) as we could use more engineers like you in our ranks :)

Feel free to leave a comment below or shoot me an email at [alex@alexbevi.com](mailto:alex@alexbevi.com) if you have any questions.
