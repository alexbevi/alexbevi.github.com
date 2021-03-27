---
layout: post
title: "Technical Services Engineering at MongoDB"
date: 2018-10-01 15:39:28 -0400
comments: true
categories: [mongodb]
---

The goal of this post is to provide a first hand account of what it means to be a *Technical Services Engineer* at [MongoDB](https://www.mongodb.com/careers/jobs/791258), as well as what the journey getting to this point has looked like for me.

### WHO AM I?

I have been working in Application Development and Software Engineering for nearly two decades. I started off writing desktop applications in QuickBASIC and Turbo Pascal, then eventually in VB6, VB.NET, C++ and C#. When it was time to shift focus to web development I started off with HTML/JS/CSS (as we all do :P), then in Flash/AS3, Flex, Python, Ruby/Rails and Node.js.

I have been writing software since I was a kid, starting with some automation tools for my mom's business. I then moved on to building tools to help me cheat at various games I was playing at the time, and eventually got more into emulator programming and reverse engineering. I guess you could say I've always loved solving problems programmatically, and especially enjoyed identifying opportunities for automation and custom tooling.

This led me down an informal DevOps track, as I was finding there was a need for optimization in the infrastructure layers that my applications were deployed to. This led me deeper into Linux internals, system administration and network operations.

While I was gaining these new skill-sets my primary focus was always on application development and delivery. Before coming to MongoDB I was working as a Development Lead / System Architect, but I found that my focus was always being drawn back to solving performance challenges at the infrastructure level.

<!-- MORE -->

### WHY MONGODB?

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

{% picture /images/why_tse/why_tse_001.png %}

So they're looking for people that are able to solve problems and communicate clearly. This could be a call center gig after all ... oh wait, *experts in MongoDB related database servers, drivers, tools, services* ... hrm, maybe there's a bit more to this.

{% picture /images/why_tse/why_tse_002.png %}

*Architecture, performance, recovery, security*, those are a lot more complex than what you would face in a traditional support role. What really sold me though was the *contribute to internal projects* statement, as this aligned perfectly with my desire for process improvement through custom tooling.

{% picture /images/why_tse/why_tse_003.png %}

By the time I got to this point in the job posting I was already sold. MongoDB is either trying to staff their first tier support with ridiculously over-qualified employees, or Technical Services really isn't what I would have thought.

I proceeded to fill out the application, attach my resume and cover letter and crossed my fingers.

### WHAT'S A TECHNICAL SERVICES ENGINEER IN PRACTICE

After working with other TSEs for the past two months and having had an opportunity to handle some of my own cases I think I can shed a bit of light on what this role really entails.

#### HOW IS IT A SUPPORT ROLE?

A Technical Services Engineer interacts with MongoDB's clients via a support queue. This allows incoming "cases" to be prioritized and categorized to allow engineers to quickly identify what form of subject matter expertise may be required (ex: `Indexing`, `Replication`, `Sharding`, `Performance`, `Networking`, etc).

As a TSE you're responsible for claiming cases from a queue and providing feedback in a timely fashion that is clear, concise and technically accurate.

#### HOW IS IT AN ENGINEERING ROLE?

Here's the juicy part of this job. Although replying to client requests is the "deliverable" for a TSE, how you go about reproducing their issues requires a very deep understanding of MongoDB internals, software engineering, network engineering, infrastructure architecture and technical troubleshooting.

Depending on the type of issue, a reproduction is likely in store. These involve recreating the environment (locally or in the cloud) to either benchmark or replicate the identified client challenge. There is a vast library of tools available to TSEs for these types of tasks, but on some occasions the right tool for the job may not exist.

In these cases, you have an opportunity to write your own scripts or tools to parse logs, measure performance, record telemetry or verify a hypothesis. Although MongoDB doesn't require TSEs to have any programming experience, for those like me that come from product engineering it's refreshing to know there's still an opportunity to scratch the development itch.

With each case you learn more about the inner working of the database, the tools, the drivers and OS level performance.

### CONCLUSION?

I'm leaving the closing section here as a question, as the TSE role continues to be redefined and refined as new MongoDB products come on board and new challenges present themselves.

What will likely remain constant though is the need for new engineers to have the following characteristics:

* a passion for continuing technical education
* a willingness to step outside their comfort zone
* an interest in software engineering
* an interest in network operations

I encourage you to check out MongoDB's [available jobs](https://grnh.se/dcd90aac1) if what I've described here interests you (I swear HR is not putting me up to this ...) as we could use more engineers like you in our ranks :)

Feel free to leave a comment below or shoot me an email at [alex@alexbevi.com](mailto:alex@alexbevi.com) if you have any questions.
