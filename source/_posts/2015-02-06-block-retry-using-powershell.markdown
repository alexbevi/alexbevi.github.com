---
layout: post
title: "Block Retry using Powershell"
date: 2015-02-06 09:54:28 -0500
comments: true
sharing: true
categories: [powershell, scripting]
---

I've been doing a lot of [Powershell](http://en.wikipedia.org/wiki/Windows_PowerShell) scripting lately, and one of the features I've really been pining for is the ability to apply some form of retry logic to either a function or a block.

Take the following sample:

``` powershell
function RandomlyFail
{
    $rnd = Get-Random -minimum 1 -maximum 3
    if ($rnd -eq 2) {
        throw "OH NOES!!!"
    }
    $Host.UI.WriteLine("W00t!!!")
}
```

Depending on what the random number we get is, we'll get one of two scenarios:

    # Success
    RandomlyFail

    W00t!!!

    # Failure
    RandomlyFail

    OH NOES!!!
    At line:62 char:9
    +         throw "OH NOES!!!"
    +         ~~~~~~~~~~~~~~~~~~
        + CategoryInfo          : OperationStopped: (OH NOES!!!:String) [], RuntimeException
        + FullyQualifiedErrorId : OH NOES!!!

Now, if this happened to be part of a larger script and we didn't have everything wrapped in a `try..catch` block, execution could potentially stop there.

Since Powershell supports [closures](http://en.wikipedia.org/wiki/Closure_%28computer_programming%29), we can write a function that accepts a [script block](http://blogs.technet.com/b/heyscriptingguy/archive/2013/04/05/closures-in-powershell.aspx) as a parameter.

<!-- more -->

{% gist alexbevi/34b700ff7c7c53c7780b %}

Now, if we retrofit our sample above:

``` powershell
Execute-With-Retry -RetryDelay 1 -VerboseOutput $true { RandomlyFail }
```

    Failed to execute [ RandomlyFail ]: OH NOES!!!
    DEBUG: Waiting 1 second(s) before attempt #1 of [ RandomlyFail ]
    Failed to execute [ RandomlyFail ]: OH NOES!!!
    DEBUG: Waiting 1 second(s) before attempt #2 of [ RandomlyFail ]
    Failed to execute [ RandomlyFail ]: OH NOES!!!
    DEBUG: Waiting 1 second(s) before attempt #3 of [ RandomlyFail ]
    Failed to execute [ RandomlyFail ]: OH NOES!!!
    DEBUG: Waiting 1 second(s) before attempt #4 of [ RandomlyFail ]
    W00t!!!
    DEBUG: Successfully executed [ RandomlyFail ]


The inspiration for this comes from an excellent article by [Pawel Pabich](http://www.pabich.eu/2010/06/generic-retry-logic-in-powershell.html).

