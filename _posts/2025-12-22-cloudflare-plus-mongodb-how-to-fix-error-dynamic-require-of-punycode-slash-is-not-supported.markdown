---
layout: post
title: "Cloudflare + MongoDB: How to fix 'Error: Dynamic require of \"punycode/\" is not supported'"
date: 2025-12-22 10:54:11 -0500
comments: true
categories: MongoDB
tags: [mongodb, drivers, node, nodejs, javascript, typescript]
image: /images/mongodb-cloudflare.png
---

If you've followed my [previous post]({% post_url 2025-03-25-cloudflare-workers-and-mongodb %}) to try and connect to MongoDB from Cloudflare workers, it's possible you've come across the following issue:

```
Error: Dynamic require of "punycode/" is not supported
```

The TL;DR is there is an issue with how `@cloudflare/vite-plugin` is [processing an import with a trailing slash within the `tr46` library](https://github.com/jsdom/tr46/pull/73), which is a transitive dependency of the MongoDB Node.js driver. The current solution is to patch this out until a proper fix is in place.

### Reproduction

Let's begin with a new application we can use as a minimum reproduction. Chances are you've already got an application ready that's hitting this issue, but if not we can verify this behavior by simply [creating a new React Router app using `create-cloudflare`](https://developers.cloudflare.com/workers/framework-guides/web-apps/react-router/) as follows, then adding the MongoDB Node.js driver as a dependency and importing it.

```bash
# create a new react router app
npm create cloudflare@latest -- my-react-router-app --framework=react-router
cd my-react-router-app
# install mongodb
npm install mongodb --save
# prepend an import to the workers/app.ts file
printf 'import { MongoClient } from "mongodb";\n%s' "$(cat workers/app.ts)" > workers/app.ts
# update wrangler.jsonc with compatibility flags to support SSR
sed -i '' '/"compatibility_date": "2025-04-04"/a\
  "compatibility_flags": ["nodejs_compat"],' wrangler.jsonc
```

With a freshly bootstrapped application, let's try running it to see what happens.

```bash
npm run dev
> dev
> react-router dev

11:15:07 AM [vite] (ssr) Re-optimizing dependencies because vite config has changed
11:15:08 AM [vite] (ssr) ✨ new dependencies optimized: mongodb
11:15:08 AM [vite] (ssr) ✨ optimized dependencies changed. reloading
[vite] program reload
Error: Dynamic require of "punycode/" is not supported
    at null.<anonymous> (/Users/alex/Temp/my-react-router-app/node_modules/.vite/deps_ssr/chunk-PLDDJCW6.js:11:9)
    at node_modules/tr46/index.js (/Users/alex/Temp/my-react-router-app/node_modules/tr46/index.js:3:18)
    at __require2 (/Users/alex/Temp/my-react-router-app/node_modules/.vite/deps_ssr/chunk-PLDDJCW6.js:17:50)
    at node_modules/whatwg-url/lib/url-state-machine.js (/Users/alex/Temp/my-react-router-app/node_modules/whatwg-url/lib/url-state-machine.js:2:14)
    at __require2 (/Users/alex/Temp/my-react-router-app/node_modules/.vite/deps_ssr/chunk-PLDDJCW6.js:17:50)
    at node_modules/whatwg-url/lib/URL-impl.js (/Users/alex/Temp/my-react-router-app/node_modules/whatwg-url/lib/URL-impl.js:2:13)
    at __require2 (/Users/alex/Temp/my-react-router-app/node_modules/.vite/deps_ssr/chunk-PLDDJCW6.js:17:50)
    at node_modules/whatwg-url/lib/URL.js (/Users/alex/Temp/my-react-router-app/node_modules/whatwg-url/lib/URL.js:499:14)
    at __require2 (/Users/alex/Temp/my-react-router-app/node_modules/.vite/deps_ssr/chunk-PLDDJCW6.js:17:50)
    at node_modules/whatwg-url/webidl2js-wrapper.js (/Users/alex/Temp/my-react-router-app/node_modules/whatwg-url/webidl2js-wrapper.js:3:13) {
  [cause]: undefined
}
```

Vite is complaining that the dynamic require of "punycode/" is not supported. The trailing slash following "punycode" is interesting, but we should first see where it's being imported. We can do this by using [`npm ls`](https://docs.npmjs.com/cli/v7/commands/npm-ls) to quickly narrow down usage of `punycode` to the `tr46` library:

```bash
npm ls punycode
my-react-router-app@ /Users/alex/Temp/my-react-router-app
└─┬ mongodb@7.0.0
  └─┬ mongodb-connection-string-url@7.0.0
    └─┬ whatwg-url@14.2.0
      └─┬ tr46@5.1.1
        └── punycode@2.3.1
```

Inspecting the `tr46` library at [https://github.com/jsdom/tr46/blob/main/index.js](https://github.com/jsdom/tr46/blob/main/index.js) shows the trailing slash on the import as well:

```js
"use strict";

const punycode = require("punycode/"); // <--- this is the line in question
const regexes = require("./lib/regexes.js");
const mappingTable = require("./lib/mappingTable.json");
const { STATUS_MAPPING } = require("./lib/statusMapping.js");
// ...
```

I initially tried to open a PR at [https://github.com/jsdom/tr46/pull/73](https://github.com/jsdom/tr46/pull/73) to sort this out, but the maintainer points out that the issue is with Vite, so we'll need to look elsewhere for a solution. This change (introduced in commit [`fef6e95`](https://github.com/jsdom/tr46/commit/fef6e95243caaa0e46a1aa42fa21af6caef11e51)) was likely done to address `punycode` deprecation warnings such as that described in [https://github.com/jsdom/tr46/issues/63](https://github.com/jsdom/tr46/issues/63). For more info on those deprecations see ["Solving the \"Punycode Module is Deprecated\" Issue in Node.js"](https://medium.com/@asimabas96/solving-the-punycode-module-is-deprecated-issue-in-node-js-93437637948a).

### Patching

We're going to solve this issue in a roundabout fashion using [`patch-package`](https://www.npmjs.com/package/patch-package) to modify the `punycode` import directly in our `node_packages` and then have a `postinstall` script that will ensure the patch is consistently applied.

```bash
# install patch-package
npm install patch-package
# update package.json to run patch-package as well as cf-typegen (which is there by default)
npm pkg set scripts.postinstall="patch-package && npm run cf-typegen"
# update node_modules/tr46/index.js to remove the trailing slash from the import
sed -i '' 's/require("punycode\/")/require("punycode")/g' node_modules/tr46/index.js
# create a patch for the tr46 package based on the above change
npx patch-package tr46
# reinstall and apply patches
npm install
```

That should do it! When we run `npm install` it will also run the `postinstall`, which will apply the patch we just created.

### Summary

Though patching transient dependencies to work around an issue like this is not ideal, it does offer a path forward for anyone hitting this specific error. To summarize what we did to address the issue:

1. Install the `patch-package` library (`npm install patch-package`)
2. Update your `package.json`'s `scripts.postinstall` to prepend a `patch-package` script to any `postinstall` scripts that may already be present
3. Modify `node_modules/tr46/index.js` to remove the trailing `/` from `require("punycode/")`
4. Create the patch by running `npx patch-package tr46`
5. Ensure the patch is applied by running `npm install`

Hopefully we can get this sorted out more cleanly (reported as [https://github.com/cloudflare/workers-sdk/issues/11751](https://github.com/cloudflare/workers-sdk/issues/11751)), but in the meantime feel free to use this approach if you find it suitable.