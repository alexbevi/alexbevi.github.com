---
layout: post
title: "Improving the Node.js Driver’s SCRAM-SHA-256 Support"
date: 2023-08-18 08:40:18 -0400
comments: true
categories: MongoDB
tags: [mongodb, drivers, nodejs, typescript, javascript]
image: /images/mongodb-logo.png
---

MongoDB always strives to offer best-in-class features, functionality, and security. A number of [authentication mechanisms](https://www.mongodb.com/docs/manual/core/authentication/#authentication-mechanisms) currently exist to verify the identity of a connecting client to your cluster, and when using the [Salted Challenge Response Authentication Mechanism (`SCRAM`)](https://www.mongodb.com/docs/manual/core/security-scram/) there are two possible hashing functions: `SCRAM-SHA-1` and `SCRAM-SHA-256`.

The [MongoDB Driver Authentication Specification](https://github.com/mongodb/specifications/blob/master/source/auth/auth.rst#defaults) outlines that when attempting to authenticate using SCRAM:
> "If `SCRAM-SHA-256` is present in the list of mechanism, then it MUST be used as the default; otherwise, `SCRAM-SHA-1` MUST be used as the default [...]".

A MongoDB Server (`mongos` or `mongod`) can be configured with a list of possible [`authenticationMechanisms`](https://www.mongodb.com/docs/manual/reference/parameters/#mongodb-parameter-param.authenticationMechanisms). As a result, MongoDB can be configured to return new authentication mechanisms which can upgrade already running applications to more secure authentication. This is the case when `SCRAM-SHA-256` is added to a cluster that previously only supported `SCRAM-SHA-1`.

Prior to hashing passwords with `SHA-256`, they will first be [prepared using SASLprep](https://datatracker.ietf.org/doc/html/rfc5802). The MongoDB Node.js driver leverages an external library ([`saslprep`](https://github.com/reklatsmasters/saslprep)) for this functionality, which was an [optional dependency](https://docs.npmjs.com/cli/v9/configuring-npm/package-json#optionaldependencies) and only used if available. Though a number of checks were in place to ensure the library was available (and loaded), an [edge case was found](https://jira.mongodb.org/browse/NODE-5289) where these checks could fail and report availability incorrectly.

## Potential Issue

Most applications won’t experience this issue, however if your Node.js project is being bundled using an alternate bundler (such as [`webpack`](https://webpack.js.org/)) it’s possible a variation of this issue may surface.

If your application was affected, it would be unable to connect to your MongoDB cluster. The stack trace from the error that would be thrown should include a call to [`continueScramConversation`](https://github.com/mongodb/node-mongodb-native/blob/51a573fe99506b81c) similar to the following examples:

```
{
  "errorType": "TypeError",
  "errorMessage": "saslprep is not a function",
  "stack": [
    "TypeError: saslprep is not a function",
    "    at continueScramConversation ([...]/index.js:xxx:yyy)",
    [...]
  ]
}
```
```
TypeError: l is not a function
    at continueScramConversation (/app/webpack:[...]/mongodb/lib/core/auth/scram.js:xxx:yy)
```

Note that [Mongoose](https://mongoosejs.com/) applications can also be affected, as Mongoose wraps the Node.js driver:

```
TypeError: (0 , o.saslprep) is not a function
    at continueScramConversation (/app/webpack:[...]/mongoose/node_modules/mongodb/lib/cmap/auth/scram.js:xxx:yy)
```

## Next Steps

The underlying issue was addressed in versions [5.7.0](https://github.com/mongodb/node-mongodb-native/releases/tag/v5.7.0), [4.17.0](https://github.com/mongodb/node-mongodb-native/releases/tag/v4.17.0) and [3.7.4](https://github.com/mongodb/node-mongodb-native/releases/tag/v3.7.4) of the MongoDB Node.js driver, so depending on the version of the driver being used by your application a minor version update will address this.

Upgrading your application’s libraries and deploying to production may not always be possible in a timely fashion. If this is the case and you happen to hit the issue described above a workaround would be to append the [`authMechanism` option](https://www.mongodb.com/docs/manual/reference/connection-string/#mongodb-urioption-urioption.authMechanism) to your connection string with a value of `SCRAM-SHA-1` as follows:

```
mongodb+srv://xyz.mongodb.net/test?authMechanism=SCRAM-SHA-1
```

This will force the driver to attempt authorization using the `SCRAM-SHA-1` hashing algorithm. Note that connection string changes would still require the application to be restarted for those changes to take effect.