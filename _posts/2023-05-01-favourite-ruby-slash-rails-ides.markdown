---
layout: post
title: "Identifying Ruby Developers' Favourite IDEs for Ruby/Rails in 2023"
date: 2023-05-01 15:38:12 -0400
comments: true
categories: [Product Management]
tags: [survey, ruby, rails]
image: /images/ruby-banner.png
mermaid: true
---

> Cross posted to [DEV](https://dev.to/alexbevi/identifying-ruby-developers-favourite-ides-for-rubyrails-in-2023-3h4k)
{: .prompt-info }

As a Product Manager, data is everything when it comes to making decisions. One of my responsibilities as a PM for Developer Interfaces is to understand how our developer communities work most effectively, and what their preferred tooling and stacks look like.

When focusing on the Ruby developer community, a simple question to ask would be _"What is your favourite editor/IDE when working with Ruby / Rails?"_ JetBrains' developer survey from 2021 found that [48% of Ruby developers mostly use RubyMine](https://www.jetbrains.com/lp/devecosystem-2021/ruby/#Ruby_what-editor-ide-do-you-mostly-use-for-ruby-development) - which may be accurate - but the survey was run by the vendor responsible for RubyMine and may have skewed results based on their sample group consisting of fans/customers/users of their products.

## Setup

I wanted to try running my own survey to see if the responses align with what JetBrains found. Since my [Reddit survey](https://www.reddit.com/r/rails/comments/12yjgwh/favorite_editoride_when_working_with_ruby_rails/) was conducted 2 years after JetBrains' how have things changed?

This was my first time running a Reddit poll, but found the community to be extremely engaged and willing to provide honest and targeted feedback. I only setup the poll to run for 72 hours, but during that time period I received:

* 931 Votes
* 20K Total Views
* 50 Upvotes
* 41 Comments

Unfortunately Reddit doesn't appear to consistently present engagement statistics (views, upvotes) so this is an approximation based on observation during the period the poll was open.

## Results

The poll contained 6 options (the maximum Reddit allows) and was open from 2023-04-25 to 2023-04-28.

```mermaid
pie title Favourite Editors for Working with Ruby/Rails
  "RubyMine": 244
  "Visual Studio Code": 418
  "Vim/Neovim": 145
  "SublimeText": 62
  "Emacs": 25
  "Other": 37
```

Based on feedback I'd received in the comments I updated [Vim](https://www.vim.org/) to also include [Neovim](https://neovim.io/), however I'd have preferred to keep these options separate.

The fact that [Visual Studio Code](https://code.visualstudio.com/) was almost half of the poll's respondents favourite editor wasn't surprising, however over a quarter still favoured [RubyMine](https://www.jetbrains.com/ruby/). This is far less that what JetBrains found, but my sample size is much smaller and audience potentially more diverse. Still the size of the user base for RubyMine is large enough that it should not be discounted when developing strategies when discussing developer tooling for Ruby specifically!

Also minor fun fact since the topic here is Ruby developer tooling. This blog is built using [Jekyll](https://jekyllrb.com/), and the chart above was created using [Mermaid](https://mermaid.js.org/) and a script similar to the [jekyll-mermaid](https://github.com/jasonbellamy/jekyll-mermaid) plugin using a code block like the one below:

```
pie title Favourite Editors for Working with Ruby/Rails
  "RubyMine": 244
  "Visual Studio Code": 418
  "Vim/Neovim": 145
  "SublimeText": 62
  "Emacs": 25
  "Other": 37
```

## Outcome

The goal of this exercise was to learn 2 things specifically:

**Based on Reddit, what are Ruby developers favourite IDEs or Editors**

The main IDEs/Editors currently favoured by the users I polled were Visual Studio Code, Neovim and RubyMine. I had an entry in the poll of _"Other"_, which I believe (based on the comments) is as follows:

* [Textmate](https://macromates.com/)
* [Atom](https://github.com/atom)
* [IntelliJ IDEA](https://www.jetbrains.com/idea/)
* [Notepad++](https://notepad-plus-plus.org/)

Developers also seem to prefer editors that support [Solargraph](https://solargraph.org/) for Intellisense.

**Is Reddit a good platform for this type of exercise**

Depending on the community/subreddit you choose to run the poll in your mileage may vary. The [r/rails](https://www.reddit.com/r/rails/) subreddit has 57K users, so the chances of getting decent engagement were moderate, and given that I only ran this poll for 3 days I feel the response rate was quite high.

I will definitely use this method again in the future.

## Conclusion

When promoting this poll I posted to LinkedIn and Twitter only. Some of the feedback I got alluded to Reddit potentially discouraging some participation as users may not have accounts and may not want to create an account just to vote in a poll. Further to this, Reddit limits the number of items you can include in your poll to 6 items and it seems [this is by design and won't be increased any time soon](https://www.reddit.com/r/ModSupport/comments/hach42/why_is_there_a_6choice_poll_limit/).

Being able to capture feedback from participants without there being a barrier to entry (like creating an account on Reddit) may improve engagement, however there is definite value in targeting a poll directly to the community represented in a subreddit.