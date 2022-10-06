---
layout: post
title: "From Engineering to Product Management"
date: 2022-10-06 03:13:27 -0400
comments: true
categories: Personal
tags: ["mongodb", "ruby", "product management"]
---

I've spent my entire professional career as an engineering IC either churning out code, working on architectural challenges or helping to lead engineering teams (while still churning out code). When I recently [moved into a Product Management role]({% post_url 2022-07-04-hello-product-management %}) at MongoDB I brought a significant amount of technical expertise about MongoDB's products with me, however I've been unsure as to how much of an advantage this really was.

Moving into Product Management is a career trajectory change, and though having an engineering background and product experience _should_ be an advantage, it can also be a disadvantage if you bring along biases, unfounded expectations and a general sense of "knowing more about something based on only _your_ experience with it".

Product Management is not only about knowing how the product works, but also about understanding the users, community, developers, competitive landscape, associated technologies, potential partners, existing customers, potential customers, the product's legacy and history (warts and all) and how to enable all these different groups to succeed. I've also been reading [Cracking the PM Career](https://www.crackingthepmcareer.com/) lately, which is helping fill in some gaps in my knowledge of this role.

This post is meant to capture some of the lessons learned in the first 90 days on the job and hopefully help anyone else considering a similar career change.

### Don't try to hit the ground running

Having used MongoDB for nearly a decade, and having worked as a [Technical Services Engineer]({% post_url 2018-10-01-technical-services-engineering-at-mongodb %}) for 3 years I understood the product suite quite well. This included the MongoDB Server, MongoDB Atlas, Atlas Realm and the ins and out of core concepts such as replication, sharding, query performance, query tuning, indexing, the aggregation pipeline, etc. I've also been building software using the MongoDB Ruby driver for a number of years, so taking over as the Product Manager for the driver seemed like a great fit.

The problem however is that having this experience resulted in bias. My experience with the product is not necessarily our users/customers experience with the product. I put a lot of pressure on myself to start delivering quickly as I should "know how things work", but new PMs on a team need to go through a discovery process - which I also ended up doing and found extremely valuable.

I went through a process similar to the _Discover -> Define -> Design -> Develop -> Deliver -> Debrief -> (REPEAT)_ cycle, which involved doing a bunch of user-focused research to try and better understand the _current_ state of our users exposure to my product during their developer journey. I know how to use the Ruby driver - I know where to look for documentation - I know where the code is ... but is that true for all of our users? How easy is it to get started? What do they find when they search for tutorials and getting started resources? Does the information they find actually help them?

The answers to the above questions would help inform a strategy that we can plan to execute against.

### Understand what your product is and isn't

MongoDB Drivers (as a product) are a little different than traditional products. They exist to act as an interface between a developer and their database, but should largely be "out of the way". A good driver will conform to the associated programming language's conventions and best practices. A Ruby programmer working with the MongoDB Ruby driver shouldn't have to adapt their codebase to work with our tools - our tools should fit neatly into their codebase.

As most Ruby applications are Ruby on Rails applications, the Mongoid ODM should allow developers to interact with their data using similar APIs that any other Active Record provider they choose for the application would expose.

I love the Ruby driver. I write most of my test cases and scenarios using the Ruby driver ... but most of our users write Rails applications and would be using the Mongoid ODM as a result. Understanding how users interact with the product, what tools and frameworks they use alongside the product and what types of issues they face really helps to highlight where I should be focusing our efforts.

### Outcomes over output

Developing a strategy is a lot harder than I expected. I'm used to measuring progress (and success) based on basic telemetry. How many cases did I take? How many cases did I close? How many tickets did I take? How many user stories did I complete? Did I push my code to prod?

The world of Product Management moves a lot slower - and for good reason. User outreach, user research, discovery, planning, interviews, writing specification, writing content, writing documentation - these all take time. Measuring the impact of the work being done also takes time, and this can be particularly challenging if you're used to a faster feedback loop.

Learn to measure incremental progress towards larger goals!

### Imposter syndrome comes for us all

Having been an engineer at MongoDB for a number of years, I assumed I'd understand how to succeed at my new role quickly. When it didn't feel like that was the case it can be hard to reach out for help - but we're all human and your colleagues want you to succeed as much as you do ;)

Initially I found myself slipping back into doing more engineering-focused tasks as that's what I was most comfortable with. Because I wasn't sure how to measure success in a Product Management capacity, this felt "safe" and also allowed me to feel productive. This only happened periodically during the first few weeks of ramping up into the new role as I was comfortable enough to reach out to colleagues and ask questions and get advice.

I've always felt like a good engineer, but I didn't feel like a good PM right away (still don't ... but working on it).

### Learn where to leverage past experience

Understanding the product and having engineering experience is beneficial to a Product Manager as it allows you to more realistically estimate the complexity of a given task/feature/epic. Being able to talk to your developers intelligently about the contents of the current sprint, offering useful feedback during stand-ups, planning and code reviews helps establish clout.

Don't assign yourself arbitrary engineering tasks though. That's not what you're there for. I fell into this trap initially and would see tickets I could "just deal with", but that's not the value of a PM to the team.

Currently I'll take tickets only if they'll help me understand the product, our users or the community better (such as documentation improvement or defect validation).

### Focus on the role

Being a PM is a new experience for me. I've never done this job before and I don't claim to be an expert at it. There is a lot to learn still and in order to do that time needs to be allocated to continuing education.

I initially tried to "pick things up as I went", but without proper focus and dedication you can get caught up in the whirlwind of the day. I block off an hour a day to just read, during which time I either focus on a particular book, scope documents, specifications, tickets, process documents, blog posts or other targeted content that will help me advance my understanding of the role.

That's it for now. If you've recently moved from Engineering to Product, or have a similar experience you want to share feel free to drop me a line and let me know how your journey is progressing.


