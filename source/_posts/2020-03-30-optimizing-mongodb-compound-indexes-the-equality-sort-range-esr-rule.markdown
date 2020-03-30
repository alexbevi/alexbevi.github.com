---
layout: post
title: "Optimizing MongoDB Compound Indexes - The \"Equality - Sort - Range\" (ESR) Rule"
date: 2020-03-30 07:35:11 -0400
comments: true
categories: [mongodb]
---

Working in Technical Services as MongoDB I find that time and again customers need assistance understanding why the indexes they've created may not be performing optimally. When providing customers with supplementary documentation, the go-to article is ["Optimizing MongoDB Compound Indexes"](https://emptysqua.re/blog/optimizing-mongodb-compound-indexes/) by MongoDB's [A. Jesse Jiryu Davis](https://emptysqua.re/blog/about/). Although this article was written in 2012, the information therin is still applicable and accurate.

This article will be heavily inspired by Jesse's article and attempt to update some examples for more modern MongoDB versions as well as focus more on how applying these "rules" can improve performance of diagnosed slow operations.