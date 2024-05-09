---
layout: post
title: "Do Not Use Mutexes in Finalizers"
date: 2024-05-09 13:27:41 -0400
comments: true
categories: Programming
tags: [ruby]
image: /images/ruby-banner-2.jpg
canonical_url: https://comandeo.dev/2023/01/01/mutexes-in-finalizers.html
author: dmitry
---

> Reposted from [Dmitry's blog](https://comandeo.dev/2023/01/01/mutexes-in-finalizers.html). Canonical URL points to his original post.
{: .prompt-tip }

Ruby allows a developer to specify a _finalizer_ proc for an object. This proc is called after an object was destroyed. This is a very useful mechanism that can be used for some cleanup when the object is gone. However, it turned out that there are limitations to what you can do inside finalizers. And these limitations are the same as ones for a signal trap. So, if you write a finalizer, you should follow the [documentation for signal traps](https://github.com/ruby/ruby/blob/master/doc/signals.rdoc).

Some time ago a user opened an issue in our bug tracker. In his logs he noticed an exception raised by the MongoDB Ruby driver:

```
`synchronize': can't be called from trap context (ThreadError)
```

From the logs, we could see that the exception was raised when calling synchronize on a mutex inside the finalizer. However, the exception says that synchronize can’t be called from a "trap context". What is that, and how is it related to our finalizers?

Finalizer is a proc that will be called when a specific object is about to be destroyed by garbage collection. In the MongoDB Ruby driver, we use finalizers to close unused cursors. A cursor is returned in response to a query and can be iterated to retrieve results. Cursors are a very convenient mechanism; however, cursors are server-side objects, and every cursor consumes server memory. Therefore, it is a good idea to let the server know if a cursor is unused so that the resources are released. So, if an object that represents a cursor is destroyed, the cursor is definitely unused and can be closed.

Below is a very simplified example of how this can be done:

```ruby
class Cursor
  def self.finalize(cursor_id, database, collection)
    proc do
      puts "Killing cursor #{cursor_id} on #{database}.#{collection}"
      # Execute command to close cursor
    end
  end

  def initialize(database, collection)
    # Initialize the cursor
    ObjectSpace.define_finalizer(
      self,
      self.class.finalize(@id, @database, @collection)
    )
  end
end
```

We can ask Ruby to do the garbage collection by calling `GC.start`, so we can test the code.

```ruby
5.times { Cursor.new('database', 'collection') }
GC.start

# => Killing cursor 258 on database.collection
# => Killing cursor 938 on database.collection
# => Killing cursor 791 on database.collection
# => Killing cursor 705 on database.collection
# => Killing cursor 114 on database.collection
```

So far so good. Of course, this solution is far from ideal. Here we send a command to the server every time the finalizer is called. First, this will block the main thread. Further, it will issue one command per cursor, which is not ideal. We can also reduce the number of commands we send by killing all cursors for a collection in one command. So, we came up with an idea for the cursor reaper — a background thread that wakes up from time to time and kills unused cursors:

```ruby
class CursorReaper
  Task = Struct.new(:id, :database, :collection)

  def initialize
    @mutex = Mutex.new
    @tasks = []
  end

  def schedule(id, database, collection)
    @mutex.synchronize do
      @tasks << Task.new(id, database, collection)
    end
  end

  def kill_cursors
    @mutex.synchronize do
      while task = @tasks.pop
        puts "Killing cursor #{task.id} on #{task.database}.#{task.collection}"
        # Group cursors per collection
      end
    end
    # Execute commands to close cursors
  end
end

class Cursor
  def self.finalize(id, database, collection, reaper)
    proc do
      reaper.schedule(id, database, collection)
    end
  end

  def initialize(database, collection, reaper)
    # Initialize the cursor
    ObjectSpace.define_finalizer(
      self,
      self.class.finalize(@id, @database, @collection, reaper)
    )
  end
end
```

Note that there is a mutex in the CursorReaper class. The kill_cursors method of the reaper will be called in a background thread, hence the locking. Let’s test it:

```ruby
reaper = CursorReaper.new
reaper_thread = Thread.new do
  loop do
    sleep(1)
    reaper.kill_cursors
  end
end

5.times { Cursor.new('database', 'collection', reaper) }
GC.start
reaper_thread.join

# => Killing cursor 205 on database.collection
# => Killing cursor 847 on database.collection
# => Killing cursor 284 on database.collection
# => Killing cursor 609 on database.collection
# => Killing cursor 485 on database.collection
```

Still, no error, even though the latter example calls synchronize inside the finalizer. What is the difference between the example and the real-world situation? In the example, we trigger garbage collection manually. Normally this is triggered by Ruby itself. What if we create so many objects that Ruby actually starts the GC?

```ruby
reaper = CursorReaper.new
reaper_thread = Thread.new do
  loop do
    sleep(1)
    reaper.kill_cursors
  end
end
populator_thread = Thread.new do
  loop do
    5000.times { Cursor.new('database', 'collection', reaper) }
    sleep(1)
  end
end
[reaper_thread, populator_thread].map(&:join)
```

Yes, this code actually reproduces the problem, and the exception is raised! So, it looks like finalizers are executed inside a signal trap. Therefore, to fix the problem we should just [follow the documentation](https://github.com/ruby/ruby/blob/master/doc/signals.rdoc) and not use operations that are not allowed inside the traps. In our case with the cursor reaper, we got rid of mutexes in finalizers by using a queue data structure, and the bug was fixed.

## We Need to Go Deeper

Even though the problem was gone, I decided to find out whether finalizers are really executed inside a signal trap. I though maybe Ruby VM uses signals internally to trigger garbage collection. I could not find any mentions about such a usage of signals, so I had to read Ruby source code. It tuned out to be fun, and the outcome was very unexpected!

I started by finding where the error _"can’t be called from trap context"_ is raised. I found it in `do_mutex_lock` function inside `thread_sync.c` file:

```c
/* When running trap handler */
if (!FL_TEST_RAW(self, MUTEX_ALLOW_TRAP) &&
  th->ec->interrupt_mask & TRAP_INTERRUPT_MASK) {
  rb_raise(rb_eThreadError, "can't be called from trap context");
}
```

So, what is actually verified is whether the execution context has a `TRAP_INTERRUPT_MASK` flag set. This flag is set in three functions: `rb_postponed_job_flush` in `vm_trace.c`, `rb_threadptr_execute_interrupts` in `thread.c`, and `signal_exec` in `signal.c`. After some debugging, I found out that in our case the flag is set in the `rb_postponed_job_flush` function. Actually, this is also confirmed by this comment for the `rb_gc` function in `gc.h`:

```
* Finalisers are deferred until we can handle interrupts. See * `rb_postponed_job_flush` in vm_trace.c.
```

Alright, now it is more or less clear what is going on. Finalizers are not executed immediately after an object is "garbage collected". Instead, a postponed job is created and scheduled. Such jobs are executed in the `rb_postponed_job_flush` function. This function sets the `TRAP_INTERRUPT_MASK` flag, which is later checked by `do_mutex_lock`. Hence the error. I even found [the commit](https://github.com/ruby/ruby/commit/05459d1a33db59c47e98e327c9f52808ebc76a3f) that introduces the current behavior, and [a bug](https://bugs.ruby-lang.org/issues/10595) that was fixed by this commit. It looks like the Ruby team wanted to make sure that finalizers are never interrupted by a signal; as a side effect, code inside finalizers is treated as code inside a signal trap.

_To summarize, finalizers are **not** executed inside a signal trap; however, Ruby applies the same restrictions to signal traps and finalizers. This is not documented anywhere; further, the exception raised is a bit misleading. Be careful!_

P.S. It is still unclear why we did not see the exception when we trigger the garbage collection manually. I wasn’t able to find the answer; maybe this is a topic for my next article.