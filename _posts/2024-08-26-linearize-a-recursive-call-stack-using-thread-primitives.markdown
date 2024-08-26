---
layout: post
title: "Linearize a Recursive Call Stack Using Thread Primitives"
date: 2024-08-26 12:57:14 -0400
comments: true
categories: Programming
tags: [ruby]
image: /images/ruby-banner-2.jpg
canonical_url: https://medium.com/@MongoDB/linearize-a-recursive-call-stack-using-thread-primitives-6c56b16d213a
author: adviti
---
# Linearize a Recursive Call Stack Using Thread Primitives

> Written by [Adviti Mishra](https://www.linkedin.com/in/advitimishra/), an intern on the MongoDB Ruby driver team
{: .prompt-tip }

[Mongoid](https://www.mongodb.com/docs/mongoid/current/) is an object document mapper (like an ORM) built on the [MongoDB Ruby driver](https://www.mongodb.com/docs/ruby-driver/current/) that Ruby on Rails developers use to interact with their MongoDB data through model instances. When developers choose to [cascade callbacks](https://www.mongodb.com/docs/mongoid/current/reference/associations/#cascading-callbacks), if their document has a large number of [embedded documents](https://www.mongodb.com/docs/mongoid/current/reference/associations/#embedded-associations), they might encounter a `SystemStackError`. In this article, we walk through how we used [Fibers](https://docs.ruby-lang.org/en/master/Fiber.html) — a lightweight thread primitive — in a non-concurrency related context of recursion to address this issue!

## **Background**

MongoDB is a document database that's designed for scalability, flexibility, and high availability. It's a non-relational database that uses JSON-like documents to store data.

Using Mongoid, Ruby on Rails developers working with MongoDB can leverage [ActiveRecord](https://guides.rubyonrails.org/active_record_basics.html)-like referential associations as well as a directly embeddable variation known as embedded associations. Let's first explore one type of document: embedded documents.

### **Embedded documents**

Developers can store related data together by *embedding* these documents in their parent model. This enables them to retrieve the associated data in a single query.

In our example we will use throughout the article, we define a Parent class, a Child class, and a Grandchild class that contain embedded associations. First, we will create a parent document that *embeds* two children documents with the first child, *embedding* two grandchildren documents.

The document representation in MongoDB would look something like this:

```json
{
  "_id": "66a926dcca8ca12bf6813902",
  "children": [
    {
      "_id": "66a926dcca8ca12bf68138fe",
      "grand_children": [
        {
          "_id": "66a926dcca8ca12bf6813900",
          "who_am_i": 0
        },
        {
          "_id": "66a926dcca8ca12bf6813901",
          "who_am_i": 1
        }
      ],
      "who_am_i": 0
    },
    {
      "_id": "66a926dcca8ca12bf68138ff",
      "who_am_i": 1
    }
  ]
}
```

This document was generated as follows:

```ruby
require 'bundler/inline'
gemfile do
  source 'https://rubygems.org'

  gem 'mongoid', '9.0.0'
end

Mongoid.configure do |config|
  config.clients.default = { uri: "mongodb://localhost:27017" }
end

# to indicate around callbacks should be fired for embedded documents
Mongoid.around_callbacks_for_embeds = true

# Initial model definitions
class Example
  include Mongoid::Document

  field :who_am_i, type: Integer
end
class Parent < Example
  embeds_many :children, cascade_callbacks: true
end
class Child < Example
  embeds_many :grandchildren, cascade_callbacks: true
end
class Grandchild < Example; end

parent = Parent.new

# Build and embed 2 child documents
parent.children = 2.times.map do |i|
  Child.new(who_am_i: i)
end

# Build and embed 2 Grandchild documents for the first child
parent.children.first.grandchildren = 2.times.map do |i|
  Grandchild.new(who_am_i: i)
end

parent.save
```

Now, let's say that every time the parent document is saved, we want to perform some logic on the parent document before, after, and around the save operation. An example of this would be logging the beginning of the operation, calculating and storing the time taken by the save operation, and logging the end of the operation. How exactly can we *hook* into this stage of the document lifecycle?

### **Callbacks**

**Callbacks**, in the context of a Mongoid application, are hooks into the lifecycle of a document's persistence context. These hooks enable developers to perform logic before, after, and/or around (immediately before and immediately after) document lifecycle events like validate, create, update, save, and destroy.

Let's modify our Example base class definition to include hooks into the before, after, and around events of the document's _"save"_ lifecycle.

```ruby
class Example
  include Mongoid::Document

  field :who_am_i, type: Integer

  # callbacks for the save operation
  before_save { puts "[#{self.class.name} #{self.who_am_i}] before callback" }
  around_save :log_around
  after_save  { puts "[#{self.class.name} #{self.who_am_i}] after callback" }

  private

  def log_around
    puts "[#{self.class.name} #{self.who_am_i}] around callback (begin)"
    yield # to yield control to the code block performing the save operation
    puts "[#{self.class.name} #{self.who_am_i}] around callback (end)"
  end
end
```

Mongoid depends on [ActiveRecord's callbacks](https://guides.rubyonrails.org/active_record_callbacks.html) implementation, with the relevant API for executing callbacks being [`Mongoid::Interceptable#run_callbacks`](https://www.rubydoc.info/github/mongoid/mongoid/Mongoid%2FInterceptable:run_callbacks). In our example, when `run_callbacks` is triggered, it will execute the `before_save` and `around_save` callbacks around the execution of the save operation, followed by the `after_save` callback.

The `yield` keyword in Ruby used when executing around callbacks is key.

Given that embedded documents are often used to store related data, sometimes, we may want the callbacks of embedded documents to run whenever a persistence operation is performed on the parent document. This phenomenon is known as **cascading callbacks.**

💡 **Illustration to build intuition:**

To illustrate how the callbacks *cascade* through the embedded documents, when we run the sample code above, the call to `parent.save` would produce the following output:

![](/images/adviti-01.png)

Having gained a better understanding of how callbacks cascade for embedded documents, we will now work on the implementation for the same. The task of running callbacks on embedded documents is abstracted away in a private API called [`Mongoid::Interceptable#_mongoid_run_child_callbacks_with_around`](https://github.com/mongodb/mongoid/blob/v9.0.0/lib/mongoid/interceptable.rb#L161-L187) and will be the function we will be working with moving forward.

## **Existing implementation (Mongoid 9.0.0 and earlier)**

Before we start coding, let's first set some goals for our implementation and enumerate what `_mongoid_run_child_callbacks_with_around` needs to know:

1. If an around callback is defined, execution needs to pause at yield and resume after the yielded logic is done executing.
2. All cascadable embedded documents need to have their callbacks executed.

The implementation must also be elegant, readable, and simple to reason about so that working with it feels good (like [Matz tells us working with Ruby should](https://www.artima.com/articles/the-philosophy-of-ruby)).

Next, let's dive into the parameters `_mongoid_run_child_callbacks_with_around` expects:

1. `kind`: the kind of callbacks to run (e.g., save, create, validate, etc.)
2. `children`: the list of embedded documents to run the callbacks on
3. `block`: executes the persistence operation the callbacks are being run for; this can either happen directly or after running any other callbacks

Equipped with this, we will first analyze the [old recursive implementation](https://github.com/mongodb/mongoid/blob/v9.0.0/lib/mongoid/interceptable.rb#L161-L187):

```ruby
def _mongoid_run_child_callbacks_with_around(kind, children: nil, &block)
  child, *tail = (children || cascadable_children(kind))
  with_children = !Mongoid::Config.prevent_multiple_calls_of_embedded_callbacks
  if child.nil?
    block&.call
  elsif tail.empty?
    child.run_callbacks(child_callback_type(kind, child), with_children: with_children, &block)
  else
    child.run_callbacks(child_callback_type(kind, child), with_children: with_children) do
      _mongoid_run_child_callbacks_with_around(kind, children: tail, &block)
    end
  end
end
```

This function handles three cases:

1. There are zero embedded documents (`child.nil?`), and if a code block was provided, it will be run.
2. There is one embedded document (`tail.empty?`) and its [`run_callbacks`](https://github.com/mongodb/mongoid/blob/v9.0.0/lib/mongoid/interceptable.rb#L113-L143) function will be invoked.
3. There are more than one embedded documents, at which point `run_callbacks` will be called recursively.

This recursive use case is where we can get into trouble. If we dig into the logic, it appears that `run_callbacks` yields to the custom block passed in that invokes `_mongoid_run_child_callbacks_with_around` but with the parameter for children as the list of remaining documents (stored in `tail`).

This seems intuitive as well based on colorized output (see above), where each color corresponds to one invocation of `_mongoid_run_child_callbacks_with_around`.

To better understand how this recursive implementation can become problematic, let's adjust the number of `Child` embedded documents our sample code will generate:

```ruby
parent = Parent.new

# Build and embed 750 child documents
parent.children = 750.times.map do |i|
  Child.new(who_am_i: i)
end

# Build and embed 2 Grandchild documents for the first child
parent.children.first.grandchildren = 2.times.map do |i|
  Grandchild.new(who_am_i: i)
end

parent.save
```

Though the increased number of child embedded documents being generated may not seem like much, according to our Ruby runtime, it is… and running this example will now raise a [`SystemStackError`](https://ruby-doc.org/core-2.5.1/SystemStackError.html).

```txt
[...]/mongoid-9.0.0/lib/mongoid/config/options.rb:38:in `block (2 levels) in option': stack level too deep (SystemStackError)
        from [...]/mongoid-9.0.0/lib/mongoid/interceptable.rb:177:in `_mongoid_run_child_callbacks_with_around'
        from [...]/mongoid-9.0.0/lib/mongoid/interceptable.rb:184:in `block in _mongoid_run_child_callbacks_with_around'
        from [...]/activesupport-7.1.3.4/lib/active_support/callbacks.rb:101:in `run_callbacks'
        from [...]/mongoid-9.0.0/lib/mongoid/interceptable.rb:139:in `run_callbacks'
        from [...]/mongoid-9.0.0/lib/mongoid/interceptable.rb:183:in `_mongoid_run_child_callbacks_with_around'
        from [...]/mongoid-9.0.0/lib/mongoid/interceptable.rb:184:in `block in _mongoid_run_child_callbacks_with_around'
        from [...]/activesupport-7.1.3.4/lib/active_support/callbacks.rb:101:in `run_callbacks'
        from [...]/mongoid-9.0.0/lib/mongoid/interceptable.rb:139:in `run_callbacks'
         ... 8134 levels...
        from [...]/mongoid-9.0.0/lib/mongoid/persistable/creatable.rb:109:in `prepare_insert'
        from [...]/mongoid-9.0.0/lib/mongoid/persistable/creatable.rb:21:in `insert'
        from [...]/mongoid-9.0.0/lib/mongoid/persistable/savable.rb:27:in `save'
        from test.rb:53:in `<main>'
```

There are well-defined base cases in `_mongoid_run_child_callbacks`, so there is no way this is a case of:

```txt
a case of:
	a case of:
		a case of:
			a case of:
				a case of:
					a case of:
						a case of:
							…
```
Infinite recursion!

**So, how did the stack space get exhausted?!**

Well, in the general case, an invocation of `_mongoid_run_child_callbacks_with_around` creates a stack frame for `run_callbacks`. When `run_callbacks` eventually yields to the block passed in, this block creates a stack frame for running `_mongoid_run_child_callbacks_with_around` and so on.

As a result, there is at least one extra stack frame for every invocation of `_mongoid_run_child_callbacks_with_around` which corresponds directly to the number of embedded documents, eventually reaching a depth that results in a `SystemStackError` being raised. The number of callbacks that can be added to the stack can vary from system to system, which makes it challenging to optimize the existing approach consistently.

Maybe there's a better way to approach this …

## **Replacing recursion with fibers in Mongoid 9.0.1**

### **So, what even are fibers?**

Fibers are thread primitives that are used for implementing lightweight cooperative concurrency. These are the two methods we will be using from the Fiber API:

1. The [`Fiber#resume`](https://docs.ruby-lang.org/en/master/Fiber.html#method-i-resume) method starts/resumes running the fiber.
2. The [`Fiber.yield`](https://docs.ruby-lang.org/en/master/Fiber.html#method-c-yield) method is called from within the fiber to return control to the caller of the `Fiber#resume`. These two methods equip fibers with a feature that we will leverage. We can control the scheduling (unlike threads that are scheduled by the operating system).

Fibers are typically used in concurrent contexts. However, we thought of using these two methods to somehow run callbacks based on a [proof of concept](https://jira.mongodb.org/secure/attachment/480870/fiber-callbacks-exploration.rb) initially proposed by my mentor, [Jamis Buck](https://github.com/jamis)!

### **Approach**

To investigate this, I wanted to first answer these high-level questions:

1. **Bottom-up**: How do callbacks work at the level of ActiveSupport in Ruby on Rails through `CallbackSequence`, `CallTemplate`, `Filters`, all the way up to `run_callbacks`?
2. **Top-down**: How does Mongoid identify a persistence operation, obtain a list of the embedded documents that callbacks can be cascaded to, and cascade the right callbacks for all of them using `run_callback`?
3. **Middle-layer**: At what point within the entire flow of callbacks (discovered through one and two) can fibers be used correctly?

I spent the first few weeks of my internship understanding callbacks in the context of the holy trinity: Ruby on Rails, Mongoid, and fibers from the Ruby language. However, when my dreams started running on separate fibers that kept yielding to each other, I realized I had to touch some grass. It was when I was touching grass on a hike that I had my eureka moment — ironically inspired by recursion.

In the Programming and Data Structure class I TA'd, one mantra we would emphasize in the recursion unit was: _"Take the recursive leap of faith."_

The recursive leap of faith means:

1. Trust that the function you are implementing runs perfectly and returns the right value.
2. Solely focus on figuring out how to depend on the function.

Extrapolate this philosophy of trust to this project where `_mongoid_run_child_callbacks_with_around` depends on Ruby on Rails' ActiveSupport:

> **What if we trust that Ruby on Rails' handling of callbacks is incredibly efficient and solely focus on *how* we depend on Ruby on Rails' `run_callbacks` instead?**
{: .prompt-info }

This helped us answer Question 3 above: At what point within the entire flow of callbacks can fibers be used correctly? Within `_mongoid_run_child_callbacks_with_around` itself!

The fundamental idea underpinning the solution that I discovered is leveraging fibers in a _"hand-off"_ fashion.

```ruby
def hand_off(children, block)
  # creating fibers for each child in children
  fibers = children.map do |child|
    Fiber.new do
      puts "Fiber for #{child.who_am_i} does work (begin)"
      Fiber.yield
      puts "Fiber for #{child.who_am_i} finishes work (end)"
    end
  end

  # resumes one fiber at a time
  fibers.each(&:resume)

  # execute the block
  block&.call

  # resumes one fiber at a time in reverse
  fibers.reverse.each(&:resume)
end
```

The `fibers.each(&:resume)` line runs the fiber for the 0th child. "Fiber for 0 does work (begin)" gets printed. When execution hits the `Fiber.yield` statement, control is returned to `fibers.each(&:resume)`. This then runs the fiber for the next child. In this fashion, the work _"before"_ the yield gets executed for all the children.

Now, the actual _"work"_ can take place. Thus, `block&.call` runs.

The `fibers.reverse.each(&:resume)` line runs the fiber for the last child. _"Fiber for 1 does work (end)"_ gets printed. This then runs the fiber for the second-to-last child. In this fashion, the work _"after"_ the yield gets executed for all the children.

Does this flow seem familiar? It is a linearized version of the bottleneck in the recursive call stack from the implementation in Mongoid 9.0 (and earlier)!

* The `fibers.each(&:resume)` mimics running the before callback and the part of the around callback before the yield.
* The `block&.call` mimics running the block passed in.
* The `fibers.reverse.each(&:resume)` mimics the _"unfolding"_ of the recursive algorithm by running the part of the around callback after the yield and the after callback.

Isn't this cool? Together, we have linearized the recursive call stack using a thread primitive!

In our case, `run_callbacks` does all the work we illustrated in the code block. To effectively hand off control between the fibers, the one tweak we need to make is that the block we pass into `run_callbacks` should yield the fiber.

The solution that we arrived at looks like:

```ruby
def _mongoid_run_child_callbacks_with_around(kind, children: nil, &block)
  children = (children || cascadable_children(kind))
  with_children = !Mongoid::Config.prevent_multiple_calls_of_embedded_callbacks

  return block&.call if children.empty?

  fibers = children.map do |child|
    Fiber.new do
      child.run_callbacks(child_callback_type(kind, child), with_children: with_children) do
        Fiber.yield
      end
    end
  end

  fibers.each do |fiber|
    fiber.resume
    raise Mongoid::Errors::InvalidAroundCallback unless fiber.alive?
  end

  block&.call

  fibers.reverse.each(&:resume)
end
```

Yay! Let's now analyze how the two implementations fair for correctness and efficiency:

> **If an around callback is defined, execution needs to pause at yield and resume after the yielded logic is done executing.**
> * _Recursive implementation_: Stack frames remember where to resume execution.
> * _Fiber-based implementation_: Each fiber resumes execution from the point it yielded.

> **All cascadable embedded documents need to have their callbacks executed.**
> * _Recursive implementation_: A stack frame is created for each embedded document.
> * _Fiber-based implementation_: A fiber is created for each embedded document within one stack frame.

As demonstrated previously, the recursive implementation stops working for embedded documents in the hundreds. On the other hand, the fibers implementation works for even 10,000+ embedded documents. Thus, you don't need to worry about your application working or not working depending on the data you have (although, you should ideally not design your database to have tens of thousands of embedded documents).

The Fiber-based implementation we've discussed throughout this post was released in [Mongoid 9.0.1](https://github.com/mongodb/mongoid/releases/tag/v9.0.1) if you want to go check it out. If you're unsure how to get started with Mongoid, there are tutorials for [Ruby on Rails](https://www.mongodb.com/docs/mongoid/current/tutorials/getting-started-rails7/) and [Sinatra](https://www.mongodb.com/docs/mongoid/current/tutorials/getting-started-sinatra/) that can help start you on your journey to building something amazing with MongoDB and Ruby!