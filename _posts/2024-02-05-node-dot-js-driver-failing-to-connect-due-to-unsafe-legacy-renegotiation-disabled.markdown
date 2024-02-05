---
layout: post
title: "Node.js Driver failing to connect due to unsafe legacy renegotiation disabled"
date: 2024-02-05 09:06:53 -0500
comments: true
categories: [MongoDB]
tags: [mongodb, drivers, networking, connections]
image: /images/mongodb-logo.png
---

## Overview

In [this community forum post](https://www.mongodb.com/community/forums/t/mongoserverselectionerror-c83200000a000152-ssl-routinesunsafe-legacy-renegotiation-disabled/262568) there was a report of the [MongoDB Node.js driver](https://www.mongodb.com/docs/drivers/node/current/) failing to connect with the following error:

> `MongoServerSelectionError: C8320000:error:0A000152:SSL routines:final_renegotiate:unsafe legacy renegotiation disabled:c:\ws\deps\openssl\openssl\ssl\statem\extensions.c:922`

This error doesn't smell like a MongoDB-specific error, so digging into _"`final_renegotiate:unsafe legacy renegotiation disabled`"_ specifically lead to [this `openssl` issue](https://github.com/openssl/openssl/issues/21296) that looks to elaborate on the meaning of the error message:

> TLSv1.2 (and earlier) support the concept of renegotiation. In 2009 (i.e. after the TLSv1.2 RFC was published), a flaw was discovered with how renegotiation works that could lead to an attack. After the attack was discovered a fix was deployed to all TLS libraries. In order for the fixed version of renegotiation to work both the client and the server need to support it.
>
> The original (unfixed) version of renegotiation is known as "unsafe legacy renegotiation" in OpenSSL. The fixed version is known as "secure renegotiation". So either a peer does not have the fix, in which case it will be using _"unsafe legacy renegotiation"_, or it does have the fix in which case it will be using _"secure renegotiation"_.
{: .prompt-info }

So it seems that the error originated from OpenSSL, and "that flaw" they're alluding to was likely [CVE-2009-3555](https://nvd.nist.gov/vuln/detail/cve-2009-3555). What was particularly interesting about this issue is that it _only_ occurred when the application was run using Node.js 20, while Node.js 16 didn't exhibit any issues - so what's different between those two versions? One notable change is that [Node.js 17+ use OpenSSL 3.0 by default](https://nodejs.org/en/blog/vulnerability/openssl-november-2022) - and starting with 3.0 [secure negotiation support is required by default](https://github.com/openssl/openssl/pull/15127).

For more information on secure server-side renegotiation I'd highly recommend [this discussion](https://github.com/openssl/openssl/discussions/21747).

## Configuring OpenSSL via the Node.js Driver

A similar issue was reported on Stack Overflow for the [`axios` library](https://www.npmjs.com/package/axios), and the [solution](https://stackoverflow.com/a/74600467/195509) there was to pass `secureOptions: crypto.constants.SSL_OP_LEGACY_SERVER_CONNECT` during request creation. As `secureOptions` is an option passed to Node's [`tls.createSecureContext`](https://nodejs.org/api/tls.html#tlscreatesecurecontextoptions) API (which MongoDB [documents an example of using](https://www.mongodb.com/docs/drivers/node/current/fundamentals/connection/tls/#securecontext-example)) it should be possible to do something similar with the Node.js driver.

```js
import { MongoClient } from 'mongodb';
import { * as crypto } from 'crypto';

const client = new MongoClient("mongodb+srv://...", {
  secureContext: {
    secureOptions: crypto.constants.SSL_OP_LEGACY_SERVER_CONNECT
  }
});
```

SUCCESS! The above example allows a `SecureContext` object to be created with the `secureOptions` selected from the [enumerated OpenSSL options Node.js has defined](https://nodejs.org/api/crypto.html#openssl-options).

> Though the Node.js driver allows direct configuration of the `SecureContext` object, as other [MongoDB drivers](https://www.mongodb.com/docs/drivers/) _may not_, [DRIVERS-2823](https://jira.mongodb.org/browse/DRIVERS-2823) is being considered to ensure this type of configuration is available.
{: .prompt-tip }

## Alternative Configuration

Configuring the MongoDB Node.js driver's OpenSSL options directly is likely the preferred approach, but the Node runtime can also be configured (via [`--openssl-config=file`](https://nodejs.org/api/cli.html#--openssl-configfile)). In this, when the `node` process is executed the path to a custom OpenSSL configuration file could be provided as follows:

```bash
node --openssl-config=/path/to/openssl.conf
```

Where `openssl.conf` is setup similar to the example below:

```
nodejs_conf = openssl_init

[openssl_init]
ssl_conf = ssl_sect

[ssl_sect]
system_default = system_default_sect

[system_default_sect]
Options = UnsafeLegacyRenegotiation
```

