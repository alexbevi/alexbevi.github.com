---
layout: post
title: "Shoutcast Streaming from the Command Line"
date: 2012-07-18 08:20
comments: true
categories: [Linux, Ubuntu, Shoutcast]
---

I spend a lot of time working in a terminal, and I like to spend that time listening to music. Since I work primarly in Linux, I was hoping there would be an easy way to merge these two activities ... and it turns out there was :)

<!-- more -->

After searching around, i found a [post on the crunchbang forums](http://crunchbanglinux.org/forums/post/150587/#p150587) that provided exactly the script I was looking for.

I modified it a tiny bit to check for dependencies:

{% codeblock Linux Shoutcast Search and Streaming - shoutcast.sh lang:bash %}
#!/bin/bash
# search shoutcast and send url to radiotray or another player
# needs Bash 4, curl, [radiotray], [xsel to send url to X selection for pasting]
# (comment out line 53 "printf '%s'..." if you don't use xsel)

command -v curl > /dev/null 2>&1 || { echo "curl required." >&2; exit 1; }
command -v xsel > /dev/null 2>&1 || { echo "xsel required." >&2; exit 1; }
command -v radiotray > /dev/null 2>&1 || { echo "radiotray required." >&2; exit 1; }

# choose player (& options if necessary): radio url will be sent to it.
radioplay() {
    radiotray "$1"
#    mplayer -playlist "$1" # replace 'mplayer -playlist' to taste, $1 will hold the url
#    exec mplayer -playlist "$1" # add 'exec' if you'd rather launch player and leave script
}

# start up radiotray in background if it's not already running
# Comment out this line if you don't use radiotray.
pgrep radiotray >/dev/null || ( radiotray >/dev/null 2>&1 & )

##########################################################################
while true
do
echo "Please enter keyword(s)"
read keyword
keyword="${keyword// /%20}" # escape spaces for url
results=$( curl -s "http://www.shoutcast.com/Internet-Radio/$keyword" |awk '
BEGIN {
    RS="<div class=\"dirlist\">"
    FS=">"
}
NR < 2 {next}
{url = name = $2
sub(/^.*title=\"/,"",name)
sub(/\".*$/,"",name)
sub(/^.*href=\"/,"",url)
sub(/\".*$/,"",url)
print url,name }
' )
[[ $results ]] || { echo "Sorry, no results for $keyword"; continue;}

unset list
declare -A list # make associative array
while read url name # read in awk's output
do
    list["$name"]="$url"
done <<< "$results"

PS3='Please enter the number of your choice > '
while true
do
    select station in "${!list[@]}" 'Search Again' Quit
    do
        [[ $station = 'Search Again' ]] && break 2
        [[ $station = Quit ]] && { echo 'Goodbye...'; exit; }
        [[ $station ]] && {
        printf '%s' "${list[$station]}" | xsel --input #--clipboard  # can paste url
        radioplay "${list[$station]}"
        break
        }
    done
echo "
Last station chosen was $station ( ${list[$station]} )
"
done

done # closes loop started at line 18
exit
{% endcodeblock %}