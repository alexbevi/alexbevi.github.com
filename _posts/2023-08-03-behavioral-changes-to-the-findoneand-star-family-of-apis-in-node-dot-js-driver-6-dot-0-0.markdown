---
layout: post
title: "Changes to findOneAnd* APIs in Node.js Driver 6.0.0"
date: 2023-08-03 08:59:29 -0400
comments: true
categories: MongoDB
tags: [mongodb, drivers, nodejs, typescript, javascript]
image: /images/mongodb-logo.png
---

One exciting change that is coming in release 6.0.0 of the Node.js Driver is that the modified (or original) document targeted by a `findOneAnd*` operation will now be returned by default.

## Current State

Up until now, as opposed to returning the requested document, this family of API methods would return a [`ModifyResult`](https://mongodb.github.io/node-mongodb-native/5.7/interfaces/ModifyResult.html), which would contain the requested document in a `value` field. This design was due to these APIs leveraging the MongoDB Server’s [`findOneAndModify`](https://www.mongodb.com/docs/manual/reference/command/findAndModify/) command and wrapping the command’s [output](https://www.mongodb.com/docs/manual/reference/command/findAndModify/#output) directly.

To demonstrate, let’s adapt the code from the Driver’s documented [usage examples](https://www.mongodb.com/docs/drivers/node/current/usage-examples/) to update one document in our _movies_ collection using the [`findOneAndUpdate`](https://mongodb.github.io/node-mongodb-native/5.7/classes/Collection.html#findOneAndUpdate) API.

```js
const database = client.db("sample_mflix");
const movies = database.collection("movies");
// Query for a movie that has the title 'The Room'
const query = { title: "The Room" };
const updatedMovie = await movies.findOneAndUpdate(query,
  { $set: { "imdb.rating": 3.4, "imdb.votes": 25750 } },
  { projection: { _id: 0, title: 1, imdb: 1 }, returnDocument: "after" });
console.log(updatedMovie);
```
```
{
  lastErrorObject: { n: 1, updatedExisting: true },
  value: {
    title: 'The Room',
    imdb: { rating: 3.4, votes: 25750, id: 368226 }
  },
  ok: 1,
  '$clusterTime': {
    clusterTime: new Timestamp({ t: 1689343889, i: 2 }),
    signature: {
      hash: Binary.createFromBase64("3twlRKhDSGIW25WVHZl17EV2ulM=", 0),
      keyId: new Long("7192273593030410245")
    }
  },
  operationTime: new Timestamp({ t: 1689343889, i: 2 })
}
```

One of the options we set was a [`returnDocument`](https://mongodb.github.io/node-mongodb-native/5.7/interfaces/FindOneAndUpdateOptions.html#returnDocument) of `after`, which should return the updated document. Though the expectation may be that the function call would return the document directly, instead you would get the output above.

While the document you’re looking for can be accessed using `updatedMovie.value`, that isn’t the most intuitive experience. But changes are on the way!

## What can we do right now?

Starting with the [Node.js Driver 5.7.0](https://github.com/mongodb/node-mongodb-native/releases/tag/v5.7.0) release, a new `FindOneAnd*Options` property called [`includeResultMetadata`](https://mongodb.github.io/node-mongodb-native/5.7/interfaces/FindOneAndUpdateOptions.html#includeResultMetadata) has been introduced. When this property is set to false (default is true), the `findOneAnd*` APIs will return the requested document as expected.

```js
const updatedMovie = await movies.findOneAndUpdate(query,
  { $set: { "imdb.rating": 3.3, "imdb.votes": 25999 } },
  { projection: { _id: 0, title: 1, imdb: 1 }, includeResultMetadata: false });
console.dir(updatedMovie);
```
```
{ title: 'The Room', imdb: { rating: 3.3, votes: 25999, id: 368226 } }
```

## What about TypeScript?

If your application uses TypeScript and the MongoDB Node.js Driver, anywhere a `findOneAnd*` call is made, if the requested document is required it will be accessed via the `value` property of the `ModifyResult`. This occurs when `includeResultMetadata` is not set or when it is set to `true` (the current default value).

![](/images/product1605-02.png)

Type hinting will indicate the Schema associated with the collection that the operation was executed against. As we would expect, when the `includeResultMetadata` is changed to `false`, inline validation will indicate there’s an issue since the `value` property no longer exists on the type associated with the result

![](/images/product1605-01.png)

Attempting to compile our TypeScript project will also fail.
```
TSError: ⨯ Unable to compile TypeScript:
index.ts:31:17 - error TS18047: 'updatedMovie' is possibly 'null'.

31     console.dir(updatedMovie.value);
                   ~~~~~~~~~~~~
index.ts:31:30 - error TS2339: Property 'value' does not exist on type 'WithId<Movie>'.

31     console.dir(updatedMovie.value);
                                ~~~~~
```

This makes it incredibly easy to identify where in the code changes need to be made.

## Next Steps

If you’re using the `findOneAnd*` family of APIs in your JavaScript or TypeScript project, upgrading the MongoDB Node.js Driver to 5.7.0+ and adding the `includeResultMetadata: false` option to those API calls will allow you to adapt your application to the new behavior prior to the 6.0.0 release.

Once 6.0.0 is released, `includeResultMetadata: false` will become the default behavior. If your application relies on the previous behavior of these APIs, setting `includeResultMetadata: true` will allow you to continue to access the `ModifyResult` directly.