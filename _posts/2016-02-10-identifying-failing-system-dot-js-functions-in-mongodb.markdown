---
layout: post
title: "Identifying failing system.js functions in MongoDB"
date: 2016-02-10 15:17:56 -0500
comments: true
categories: [MongoDB]
tags: [mongodb, javascript, scripting, troubleshooting]
---

``` bash
laptop(mongod-3.2.1) test> db.loadServerScripts()
2016-02-10T15:18:42.322-0500 E QUERY    [thread1] SyntaxError: unterminated string literal :
DB.prototype.loadServerScripts/<@src/mongo/shell/db.js:1158:9
DBQuery.prototype.forEach@src/mongo/shell/query.js:477:1
DB.prototype.loadServerScripts@src/mongo/shell/db.js:1157:5
@(shell):1:1

2016-02-10T15:18:42.323-0500 E QUERY    [thread1] Error: SyntaxError: unterminated string literal :
DB.prototype.loadServerScripts/<@src/mongo/shell/db.js:1158:9
DBQuery.prototype.forEach@src/mongo/shell/query.js:477:1
DB.prototype.loadServerScripts@src/mongo/shell/db.js:1157:5
@(shell):1:1
 :
DB.prototype.loadServerScripts/<@src/mongo/shell/db.js:1158:9
DBQuery.prototype.forEach@src/mongo/shell/query.js:477:1
DB.prototype.loadServerScripts@src/mongo/shell/db.js:1157:5
@(shell):1:15:17:56
```

Occasionally we'll run into these scenarios where we need to load the `system.js` functions into the global context, but for whatever reason one (or more) scripts are borked.

I created on that essentially looks like the following to illustrate this point.

``` javascript
var thisFunctionShouldFail = function() {
    return "Fail
}
```

When you try to execute a `db.loadServerScripts()` call, the entire process will fail as there is a malformed script.

This is a major pain in the ass when you have large background processes that rely heavily on internal system scripts.

In order to address this, we wrote a small script that you can run against any database to validate the internal scripts:

``` javascript
var testSystemJs = function() {
    var coll = db.system.js;
    coll.find({}, {_id: 1}).forEach(function(doc) {
       try {
           var func = coll.findOne({_id: doc._id});
           eval(func.value);
       } catch (ex) {
           print("LOAD_ERROR: " + doc._id);
       }
    });
}
```

Now if you run the above, it will give you a bit more context into the failures you may have ;)

```
laptop(mongod-3.2.1) test> testSystemJs()
2016-02-10T15:52:13.086-0500 E QUERY    [thread1] SyntaxError: unterminated string literal :
testSystemJs/<@(shell):1:190
DBQuery.prototype.forEach@src/mongo/shell/query.js:477:1
testSystemJs@(shell):1:66
@(shell):1:1

LOAD_ERROR: thisFunctionShouldFail
2016-02-10T15:52:13.088-0500 E QUERY    [thread1] SyntaxError: unterminated string literal :
testSystemJs/<@(shell):1:190
DBQuery.prototype.forEach@src/mongo/shell/query.js:477:1
testSystemJs@(shell):1:66
@(shell):1:1

LOAD_ERROR: thisFunctionShouldAlsoFail
```

I'm testing this on a mongo 3.2.1 system, but this method should be applicable to older releases as well.