---
layout: post
title: "Generating a ScummVM Games List"
date: 2021-05-31 06:55:45 -0400
comments: true
categories: Programming
tags: [scummvm, ruby]
---

A long time ago I reached out to the ScummVM leadership about a script I'd been working on that could be used to scrape detection entries and generate a definitive games list.

![](/images/scummvm-email-detection.png)

As with most of my ScummVM-related development, this fell by the wayside for a number of years, but recently I've rekindled my love of scripting (and Ruby) so I wanted to try and get this script at least into a (somewhat) working state.

{% gist alexbevi/3425815ea17d6a14e0832bd263e97954 %}

This script just needs to be downloaded to the ScummVM source directly and run. At the time of writing this script doesn't deduplicate results and is not guaranteed to be 100% accurate, but it should be close enough to give you an idea how many great games are currently supported by ScummVM at the commit point you currently have checked out.

![](/images/scummvm-detection-ruby.png)

The results below are recent as of commit [`57e13c641e`](https://github.com/scummvm/scummvm/commit/57e13c641e):

| Engine | Title (768) |
|--------|-------|
|wintermute|1 1/2 Ritter: Auf der Suche nach der hinreissenden Herzelinde|
|toltecs|3 Skulls of the Toltecs|
|agt|A Bloody Life|
|ags|A Christmas Tale|
|ags|A Day In The Future|
|wage|A Mess O' Trouble|
|director|A Silly Noisy House|
|agi|AGI Demo|
|agi|AGI Tetris|
|ags|AGS Game Scanner|
|director|ALeX-WORLD|
|director|AMBER: Journeys Beyond|
|ags|ASAP Adventure|
|ags|Aaron's Epic Journey|
|sludge|Above The Waves|
|ags|Ace Duswell - Where's The Ace|
|director|Activision's Atari 2600 Action Pack|
|wintermute|Actual Destination|
|adrift|Adrift IF Game|
|advsys|AdvSys Game|
|ags|Adventure Game|
|ags|Adventure Game Studio Game|
|lilliput|Adventures of Robin Hood|
|alan2|Alan2 Game|
|alan3|Alan3 Game|
|director|Alice: An Interactive Museum|
|wintermute|Alimardan Meets Merlin|
|wintermute|Alimardan's Mischief|
|wintermute|Alpha Polaris|
|director|AmandaStories|
|access|Amazon: Guardians of Eden|
|director|Ankh 2: Mystery of Tutankhamen|
|director|Ankh 3|
|director|Ankh: Mystery of the Pyramids|
|wage|Another Fine Mess|
|ags|Anton Ulvfot's Mid-Town Shootout|
|wintermute|Apeiron|
|director|Arc of Doom|
|archetype|Archetype IF Game|
|wintermute|Art of Murder 1: FBI Confidential|
|director|ArtRageous!|
|sci|Astro Chicken|
|ags|BLUECUP - on the run|
|scumm|Backyard Baseball|
|scumm|Backyard Baseball 2001|
|scumm|Backyard Baseball 2003|
|scumm|Backyard Basketball|
|scumm|Backyard Football|
|scumm|Backyard Football 2002|
|scumm|Backyard Soccer|
|scumm|Backyard Soccer 2004|
|scumm|Backyard Soccer MLS Edition|
|director|Bad Day on the Midway|
|wintermute|Barrow Hill - The Dark Path|
|wintermute|Basis Octavus|
|scumm|Bear Stormin'|
|illusions|Beavis and Butt-head Do U|
|bbvs|Beavis and Butt-head in Virtual Stupidity|
|sky|Beneath a Steel Sky" ;|
|ags|Bert the Newsreader|
|wintermute|Beyond the Threshold|
|director|Beyond the Wall of Stars|
|wintermute|Bickadoodle|
|scumm|Big Thinkers First Grade|
|scumm|Big Thinkers Kindergarten|
|bladerunner|Blade Runner|
|bladerunner|Blade Runner with restored content|
|dragons|Blazing Dragons|
|tsage|Blue Force|
|scumm|Blue's 123 Time Activities|
|scumm|Blue's ABC Time Activities|
|scumm|Blue's Art Time Activities|
|scumm|Blue's Birthday Adventure|
|scumm|Blue's Reading Time Activities|
|scumm|Blue's Treasure Hunt|
|ags|Bob's Quest 2: The quest for the AGS Blue cup award|
|wintermute|Book of Gron Part One|
|ags|Book of Spells 1|
|ags|Book of Spells 2|
|ags|Book of Spells 3|
|wintermute|Boredom of Agustin Cordes|
|sword25|Broken Sword 2.5|
|sword1|Broken Sword: The Shadow of the Templars";|
|tucker|Bud Tucker in Double Trouble|
|director|Busy People of Hamsterland|
|director|Byron Preiss Multimedia Catalog|
|agi|Caitlyn's Destiny|
|ags|Calsoon|
|wage|Camp Cantitoe|
|wintermute|Carol Reed 10 - Bosch's Damnation|
|wintermute|Carol Reed 11 - Shades Of Black|
|wintermute|Carol Reed 12 - Profound Red|
|wintermute|Carol Reed 13 - The Birdwatcher|
|wintermute|Carol Reed 14 - The Fall Of April|
|wintermute|Carol Reed 15 - Geospots|
|wintermute|Carol Reed 16 - Quarantine Diary|
|wintermute|Carol Reed 4 - East Side Story|
|wintermute|Carol Reed 5 - The Colour of Murder|
|wintermute|Carol Reed 6 - Black Circle|
|wintermute|Carol Reed 7 - Blue Madonna|
|wintermute|Carol Reed 8 - Amber's Blood|
|wintermute|Carol Reed 9 - Cold Case Summer|
|ags|Carver Island 2: Mrs. Rodriguez's Revenge|
|sci|Castle of Dr. Brain|
|ags|Chamber|
|chewy|Chewy: Esc from F5|
|wintermute|Chivalry is Not Dead|
|director|Chop Suey|
|sci|Christmas Card 1988|
|sci|Christmas Card 1990: The Seasoned Professional|
|sci|Christmas Card 1992|
|director|Chu-Teng|
|groovie|Clandestiny|
|sci|Codename: Iceman|
|wintermute|Colors on Canvas|
|ags|Compensation|
|sci|Conquests of Camelot: King ArthurQuest for the Grail|
|sci|Conquests of the Longbow: The Adventures of Robin Hood|
|wintermute|Conspiracao Dumont|
|wintermute|Corrosion: Cold Winter Waiting|
|magnetic|Corruption|
|director|Cosmology of Kyoto|
|sci|Crazy Nick's Software Picks: King Graham's Board Game Challenge|
|sci|Crazy Nick's Software Picks: Leisure Suit Larry's Casino|
|sci|Crazy Nick's Software Picks: Parlor Games with Laura Bow|
|sci|Crazy Nick's Software Picks: Robin Hood's Game of Skill and Chance|
|sci|Crazy Nick's Software Picks: Roger Wilco's Spaced Out Game Pack|
|cruise|Cruise for a Corpse|
|ultima|Crusader: No Regret|
|ultima|Crusader: No Remorse|
|sludge|Cubert BadboneP.I.|
|director|DEVO Presents: Adventures of the Smart Patrol|
|wintermute|DFAF Adventure|
|composer|Darby the Dragon|
|wintermute|Dark Fall: Lost Souls|
|ags|Darts|
|scumm|Day of the Tentacle|
|wintermute|Dead City|
|ags|Deepbright|
|macventure|Deja Vu|
|macventure|Deja Vu II|
|ags|Demon Slayer 1|
|ags|Demon Slayer 2|
|ags|Demon Slayer 3|
|ags|Demon Slayer 4|
|agos|Demon in my Pocket|
|director|Derrat Sorcerum|
|wintermute|Des Reves Elastiques Avec Mille Insectes Nommes Georges|
|wintermute|Devil In The Capital|
|saga|Dinotopia|
|ags|Dirk Chafberg|
|wintermute|Dirty Split|
|tinsel|Discworld|
|tinsel|Discworld 2: Missing Presumed ...!?|
|tinsel|Discworld Noir|
|director|Don't Quit Your Day Job|
|agi|Donald Duck's Playground|
|wintermute|Dr. Bohus|
|wintermute|Dr. Doyle - Mystery Of The Cloche Hat|
|draci|Draci Historie|
|mads|Dragonsphere|
|wage|Drakmyth Castle|
|drascula|Drascula: The Vampire Strikes Back|
|dreamweb|DreamWeb|
|wintermute|Dreamcat|
|wintermute|Dreamscape|
|illusions|Duckman|
|dm|Dungeon Master|
|director|Earthtia Saga: Larthur's Legend|
|director|Earthworm Jim|
|ags|Earwig Is Angry!|
|director|Eastern Mind: The Lost Souls of Tong Nou|
|ags|Eclair 1|
|ags|Eclair 2|
|sci|EcoQuest II: Lost Secret of the Rainforest|
|sci|EcoQuest: The Search for Cetus"// floppy is SCI1CD SCI1.1|
|wintermute|Eight Squares in The Garden|
|ags|El Burro|
|agos|Elvira - Mistress of the Dark|
|agos|Elvira II - The Jaws of Cerberus|
|wage|Enchanted Scepters|
|director|Ernie|
|ags|Ernie's Big Adventure|
|ags|Ernie's Big Adventure 2|
|director|Escape from Planet Arizona|
|wintermute|Escape from the Mansion|
|wintermute|Everyday Grey|
|ags|Exile|
|kyra|Eye of the Beholder|
|kyra|Eye of the Beholder II: The Legend of Darkmoon|
|ags|Eyes of the Jade Sphinx|
|wintermute|Face Noir|
|saga|Faery Tale Adventure II: Halls of the Dead|
|wintermute|Fairy Tales About Toshechka and Boshechka|
|agi|Fanmade AGI game|
|sci|Fanmade SCI Game|
|scumm|Fatty Bear's Birthday Surprise|
|scumm|Fatty Bear's Fun Pack|
|wintermute|Finding Hope|
|ags|Firewall|
|magnetic|Fish!|
|wintermute|Five Lethal Demons|
|wintermute|Five Magical Amulets|
|queen|Flight of the Amazon Queen|
|ags|Floyd|
|wintermute|Forgotten Sound 1 - Revelation|
|wintermute|Forgotten Sound 2 - Destiny|
|wintermute|Four|
|wintermute|FoxTail|
|wintermute|Framed|
|director|Frankenstein: Through the Eyes of the Monster|
|sludge|Frasse and the Peas of Kejick|
|director|Freak Show|
|scumm|Freddi Fish 1: The Case of the Missing Kelp Seeds|
|scumm|Freddi Fish 2: The Case of the Haunted Schoolhouse|
|scumm|Freddi Fish 3: The Case of the Stolen Conch Shell|
|scumm|Freddi Fish 4: The Case of the Hogfish Rustlers of Briny Gulch|
|scumm|Freddi Fish 5: The Case of the Creature of Coral Cove|
|scumm|Freddi Fish and Luther's Maze Madness|
|scumm|Freddi Fish and Luther's Water Worries|
|scumm|Freddi Fish's One-Stop Fun Shop|
|sci|Freddy Pharkas: Frontier Pharmacist|
|ngi|Full Pipe|
|scumm|Full Throttle|
|sci|Fun Seeker's Guide|
|cine|Future Wars|
|sci|Gabriel Knight: Sins of the Fathers|
|sci|Gabriel Knight: Sins of the Fathers|
|director|Gadget: InventionTravel& Adventure|
|ags|Gaea Fallen|
|director|Gahan Wilson's The Ultimate Haunted House|
|wintermute|Ghost in the Sheet|
|glulx|Glulx Game|
|gnap|Gnap|
|agi|Gold Rush!|
|ags|Gorther of the Cave People|
|ags|Granny Zombiekiller in: Mittens Murder Mystery|
|ags|Greg's Mountainous Adventure|
|composer|Gregory and the Hot Air Balloon|
|grim|Grim Fandango|
|director|Gundam 0079: The War for Earth|
|hadesch|Hades Challenge|
|wintermute|Hamlet or the last game without MMORPG featuresshaders and product placement|
|director|Hamsterland: The Time Machine|
|wintermute|Helga Deep In Trouble|
|ags|Hermit|
|adl|Hi-Res Adventure #0: Mission Asteroid|
|adl|Hi-Res Adventure #1: Mystery House|
|adl|Hi-Res Adventure #2: Wizard and the Princess|
|adl|Hi-Res Adventure #3: Cranston Manor|
|adl|Hi-Res Adventure #4: Ulysses and the Golden Fleece|
|adl|Hi-Res Adventure #5: Time Zone|
|adl|Hi-Res Adventure #6: The Dark Crystal|
|hopkins|Hopkins FBI|
|wintermute|Hor|
|sci|Hoyle Bridge|
|sci|Hoyle Children's Collection|
|sci|Hoyle Classic Card Games|
|sci|Hoyle Classic Games|
|sci|Hoyle Official Book of Games: Volume 1|
|sci|Hoyle Official Book of Games: Volume 2|
|sci|Hoyle Official Book of Games: Volume 3|
|sci|Hoyle Solitaire|
|hugo|Hugo 1: Hugo's House of Horrors|
|hugo|Hugo 2: Whodunit?|
|hugo|Hugo 3: Jungle of Doom|
|hugo|Hugo IF Game|
|scumm|Humongous Interactive Catalog|
|director|HyperBlade|
|hdb|Hyperspace Delivery Boy!|
|saga|I Have No Mouth and I Must Scream|
|wintermute|I Must Kill...: Fresh Meat|
|sci|ImagiNation Network (INN) Demo|
|icb|In Cold Blood|
|scumm|Indiana Jones and the Fate of Atlantis|
|scumm|Indiana Jones and the Last Crusade|
|scumm|Indiana Jones and the Last Crusade & Loom|
|scumm|Indiana Jones and the Last Crusade & Zak McKracken|
|wintermute|Informer Alavi - Murder of Miss Rojan|
|saga|Inherit the Earth: Quest for the Orb|
|sci|Inside the Chest"// aka Behind the Developer's Shield|
|ags|Interface Show-off|
|director|Iron Helix|
|director|Isis|
|wintermute|J.U.L.I.A.|
|wintermute|J.U.L.I.A.: Among the Stars|
|wintermute|J.U.L.I.A.: Untold|
|director|JUMP: The David Bowie Interactive CD-ROM|
|ags|James Bondage|
|wintermute|James Peris: No License Nor Control|
|director|Jewels of the Oracle|
|ags|Jingle Bells|
|magnetic|Jinxter|
|sci|Jones in the Fast Lane|
|agos|Jumble|
|director|Just Me & My Dad|
|wintermute|K'NOSSOS|
|director|Karma: Curse of the 12 Caves|
|ags|Kidnapped|
|agi|King's Quest I: Quest for the Crown|
|sci|King's Quest I: Quest for the Crown"// Note: There was also an AGI version of this|
|agi|King's Quest II: Romancing the Throne|
|agi|King's Quest III: To Heir Is Human|
|agi|King's Quest IV: The Perils of Rosella|
|sci|King's Quest IV: The Perils of Rosella"// Note: There was also an AGI version of this|
|sci|King's Quest V: Absence Makes the Heart Go Yonder|
|sci|King's Quest VI: Heir TodayGone Tomorrow|
|sci|King's Quest VII: The Princeless Bride|
|sci|King's Questions|
|kingdom|Kingdom: The Far Reaches|
|wintermute|Kulivocko|
|director|L-ZONE|
|lab|Labyrinth of Time|
|director|Labyrinthe|
|kyra|Lands of Lore: The Throne of Chaos|
|ags|Larry Vales II: Dead Girls are Easy|
|ags|Larry Vales III: Time Heals All 'Burns|
|ags|Larry Vales: Traffic Division|
|ags|Lassi Quest I|
|ags|Lassi and Roger|
|ags|Lassi and Roger Meet God|
|sci|Laura Bow 2: The Dagger of Amon Ra|
|sci|Laura Bow: The Colonel's Bequest|
|made|Leather Goddesses of Phobos 2|
|sci|Leisure Suit Larry 2: Goes Looking for Love (in Several Wrong Places)|
|sci|Leisure Suit Larry 3: Passionate Patti in Pursuit of the Pulsating Pectorals|
|sci|Leisure Suit Larry 5: Passionate Patti Does a Little Undercover Work|
|sci|Leisure Suit Larry 6: Shape Up or Slip Out!|
|sci|Leisure Suit Larry 6: Shape Up or Slip Out!|
|sci|Leisure Suit Larry 7: Love for Sail!|
|agi|Leisure Suit Larry in the Land of the Lounge Lizards|
|sci|Leisure Suit Larry in the Land of the Lounge Lizards"// Note: There was also an AGI version of this|
|sludge|Lepton's Quest|
|scumm|Let's Explore the Airport with Buzzy|
|scumm|Let's Explore the Farm with Buzzy|
|scumm|Let's Explore the Jungle with Buzzy|
|sludge|Life Flashes By|
|wintermute|Life In 3 Minutes|
|sci|Lighthouse: The Dark Being|
|wintermute|Limbo of the Lost|
|director|Lion|
|twine|Little Big Adventure|
|ags|Little Jonny Evil|
|ags|Little Willie|
|wintermute|Looky|
|scumm|Loom|
|avalanche|Lord Avalot d'Argent|
|cryo|Lost Eden|
|director|Louis Cat Orze: The Mystery of the Queen's Necklace|
|wintermute|Lov Mamuta|
|ags|Lupo Inutile|
|lure|Lure of the Temptress|
|wintermute|Machu Mayu|
|director|Macromedia Director All Movies Test Target|
|director|Macromedia Director Game|
|director|Macromedia Director Test Target|
|director|Mad Mac Cartoons|
|ags|Mafio|
|ngi|Magic Dream|
|composer|Magic Tales|
|composer|Magic Tales: Baba Yaga and the Magic Geese|
|composer|Magic Tales: Imo and the King|
|composer|Magic Tales: Liam Finds a Story|
|composer|Magic Tales: Sleeping Cub's Test of Courage|
|composer|Magic Tales: The Little Samurai|
|composer|Magic Tales: The Princess and the Crab|
|magnetic|Magnetic Scrolls Game|
|director|Majestic Part I: Alien Encounter|
|sludge|Mandy Christmas Adventure|
|agi|Manhunter 1: New York|
|agi|Manhunter 2: San Francisco|
|scumm|Maniac Mansion|
|access|Martian Memorandum|
|director|Masters of the Elements|
|director|MechWarrior 2|
|director|Meet Mediaband|
|ags|Men In Brown|
|wintermute|Mental Repairs Inc|
|agi|Mickey\'s Space Adventure|
|director|Microsoft Bookshelf '94|
|director|Microsoft Encarta '94|
|director|Microsoft Encarta '95|
|xeen|Might and Magic IV: Clouds of Xeen|
|xeen|Might and Magic V: Darkside of Xeen|
|xeen|Might and Magic: Swords of Xeen|
|xeen|Might and Magic: World of Xeen|
|wintermute|Mirage|
|director|Mirage|
|supernova|Mission Supernova 1|
|agi|Mixed-Up Mother Goose|
|sci|Mixed-Up Mother Goose|
|sci|Mixed-Up Mother Goose|
|sci|Mixed-up Fairy Tales|
|ags|Mom's Quest|
|wintermute|Monday Starts on Saturday|
|scumm|Monkey Island 2: LeChuck's Revenge|
|ags|Monkey Plank|
|scumm|Moonbase Commander|
|ags|Moose Wars: Desire For More Cows|
|mortevielle|Mortville Manor|
|ags|Mr. Grey's Greyt Adventure|
|sci|Ms. Astro Chicken|
|director|Mummy: Tomb of the Pharaoh|
|director|Muppet Treasure Island|
|ags|Murder|
|wintermute|Murder In Tehran's Alleys 1933|
|wintermute|Murder In Tehran's Alleys 2016|
|mutationofjb|Mutation of J.B.|
|director|Mylk|
|mohawk|Myst|
|myst3|Myst III Exile|
|director|Mysterious Egypt|
|magnetic|Myth|
|wintermute|Myth: A Guff's Tale|
|nancy|Nancy Drew: Message in a Haunted Mansion|
|nancy|Nancy Drew: Secret of the Scarlet Hand|
|nancy|Nancy Drew: Secrets Can Kill|
|nancy|Nancy Drew: Stay Tuned for Danger|
|nancy|Nancy Drew: The Final Scene|
|nancy|Nancy Drew: Treasure in the Royal Tower|
|sludge|Nathan's Second Chance|
|director|Necrobius|
|ags|Nicholas Wolfe part I: Framed|
|wintermute|Night Train|
|ags|Night of the Plumber|
|ngi|Nikita Game Interface game|
|director|Nile: Passage to Egypt|
|director|Nine Worlds hosted by Patrick Stewart|
|parallaction|Nippon Safes Inc.|
|agos|NoPatience|
|director|Noir: A Shadowy Thriller|
|ags|Novo Mestro|
|wintermute|Oknytt|
|wintermute|On the Tracks of Dinosaurs|
|wintermute|One|
|wintermute|One Helluva Day|
|wintermute|Open Quest|
|director|Opera Fatal|
|cine|Operation Stealth|
|director|Operation Teddy Bear|
|director|Operation: Eco-Nightmare|
|director|Operation: Weather Disaster|
|sludge|Out Of Order|
|director|P.A.W.S.: Personal Automated Wagging System|
|wintermute|Paintaria|
|scumm|Pajama Sam 1: No Need to Hide When It's Dark Outside|
|scumm|Pajama Sam 2: Thunder and Lightning Aren't so Frightening|
|scumm|Pajama Sam 3: You Are What You Eat From Your Head to Your Feet|
|scumm|Pajama Sam's Lost & Found|
|scumm|Pajama Sam's One-Stop Fun Shop|
|scumm|Pajama Sam's Sock Works|
|scumm|Pajama Sam: Games to Play on Any Day|
|wintermute|Palladion|
|wintermute|Papa's Daughters|
|wintermute|Papa's Daughters Go to the Sea|
|director|Paradise Rescue|
|scumm|Passport to Adventure|
|sci|Pepper's Adventure in Time|
|ags|Permanent Daylight|
|ags|Perpetrator|
|agos|Personal Nightmare|
|sci|Phantasmagoria|
|sci|Phantasmagoria 2: A Puzzle of Flesh|
|director|Phantasmagoria Amusement Planet|
|wintermute|Pigeons in the Park|
|director|Pitfall: The Mayan Adventure|
|wintermute|Pizza Morgana: Episode 1 - Monsters and Manipulations in the Magical Forest|
|ags|Pizza Quest|
|plumbers|Plumbers Don't Wear Ties!|
|ags|Point Blank|
|wintermute|Pole Chudes|
|agi|Police Quest I: In Pursuit of the Death Angel|
|sci|Police Quest II: The Vengeance|
|sci|Police Quest III: The Kindred|
|sci|Police Quest IV: Open Season|
|sci|Police Quest IV: Open Season"// floppy is SCI2CD SCI2.1|
|sci|Police Quest: In Pursuit of the Death Angel"// Note: There was also an AGI version of this|
|sci|Police Quest: SWAT|
|ags|Porn Quest|
|private|Private Eye|
|wintermute|Project Joe|
|wintermute|Project Lonely Robot|
|wintermute|Project: Doom|
|scumm|Putt-Putt & Fatty Bear's Activity Pack|
|scumm|Putt-Putt Enters the Race|
|scumm|Putt-Putt Goes to the Moon|
|scumm|Putt-Putt Joins the Circus|
|scumm|Putt-Putt Joins the Parade|
|scumm|Putt-Putt Saves the Zoo|
|scumm|Putt-Putt Travels Through Time|
|scumm|Putt-Putt and Pep's Balloon-O-Rama|
|scumm|Putt-Putt and Pep's Dog on a Stick|
|scumm|Putt-Putt's Fun Pack|
|scumm|Putt-Putt's One-Stop Fun Shop|
|wintermute|Qajary Cat|
|ags|Quest For Colours|
|quest|Quest Game|
|ags|Quest for Glory 4 1/2|
|sci|Quest for Glory I: So You Want to Be a Hero"// Note: There was also a SCI0 version of this (further up)|
|sci|Quest for Glory I: So You Want to Be a Hero"// Note: There was also a SCI11 VGA remake of this (further down)|
|sci|Quest for Glory II: Trial by Fire|
|sci|Quest for Glory III: Wages of War|
|sci|Quest for Glory IV: Shadows of Darkness|
|sci|Quest for Glory IV: Shadows of Darkness"// floppy is SCI2CD SCI2.1|
|sci|RAMA|
|ags|RIPP|
|ags|Racing Manager|
|director|Ray Bradbury's The Martian Chronicles Adventure Game|
|wage|Ray's Maze|
|ags|Raymond's Keys|
|wintermute|Rebecca Carlson Mystery 01 - Silent Footsteps|
|ags|Red|
|wintermute|Red Comrades 0.2: Operation F.|
|petka|Red Comrades 1: Save the Galaxy|
|petka|Red Comrades 2: For the Great Justice|
|petka|Red Comrades Demo|
|director|Refixion|
|director|Refixion II: Museum or Hospital|
|director|Refixion III: The Reindeer Story|
|mads|Return of the Phantom|
|tsage|Return to Ringworld|
|made|Return to Zork|
|wintermute|Reversion: The Escape|
|wintermute|Reversion: The Meeting|
|wintermute|Reversion: The Return|
|mads|Rex Nebular and the Cosmic Gender Bender|
|wintermute|Rhiannon: Curse of the four Branches|
|ags|Richard Longhurst and the Box That At|
|ags|Ricky Longhurst and the Box that Ate Time|
|tsage|Ringworld: Revenge of the Patriarch|
|ags|Rob Blanc I: Better Days of a Defender of the Universe|
|ags|Rob Blanc II: Planet of the Pasteurised Pestilence|
|ags|Rob Blanc III: The Temporal Terrorists|
|sludge|Robin's Rescue|
|director|Robotoid Assembly Toolkit|
|ags|Rode Kill: A Day In the Life|
|ags|Rode Quest|
|director|Rodney's Funscreen|
|made|Rodney's Funscreen|
|ags|Rollinfoy|
|lilliput|Rome: Pathway to Power|
|wintermute|Rosemary|
|scumm|SPY Fox 1: Dry Cereal|
|scumm|SPY Fox 2: Some Assembly Required|
|scumm|SPY Fox 3: Operation Ozone|
|scumm|SPY Fox in Cheese Chase|
|scumm|SPY Fox in Hold the Mustard|
|director|Sakin II|
|scumm|Sam & Max Hit the Road|
|ags|Sam The Pirate Monkey|
|director|Santa Fe Mysteries: The Elk Moon Murder|
|wintermute|Satan and Sons|
|director|Science Smart|
|director|Scientific American Library: Illusion|
|director|Scientific American Library: The Universe|
|director|Screaming Metal|
|wintermute|Securanote|
|agi|Serguei's Destiny 1|
|agi|Serguei's Destiny 2|
|cge2|Sfinx|
|wintermute|Shaban|
|macventure|Shadowgate|
|wintermute|Shadows on the Vatican - Act I: Greed|
|wintermute|Shadows on the Vatican - Act II: Wrath|
|director|Shanghai: Great Moments|
|sci|Shivers|
|sci|Shivers II: Harvest of Souls"// Not SCI|
|agi|Sierra AGI game|
|sci|Sierra SCI Game|
|agos|Simon the Sorcerer 1|
|agos|Simon the Sorcerer 2|
|director|SkyBorg: Into the Vortex|
|ags|Slacker Quest|
|sci|Slater & Charlie Go Camping|
|sludge|Sludge Game|
|ags|Snail Quest|
|ags|Snail Quest 2|
|ags|Snail Quest 3|
|wintermute|Sofia's Debt|
|ags|Sol|
|cge|Soltys|
|ags|Space|
|wintermute|Space Invaders|
|wintermute|Space Madness|
|agi|Space Quest 0: Replicated|
|sci|Space Quest 6: The Spinal Frontier|
|agi|Space Quest I: The Sarien Encounter|
|sci|Space Quest I: The Sarien Encounter"// Note: There was also an AGI version of this|
|agi|Space Quest II: Vohaul's Revenge|
|sci|Space Quest III: The Pirates of Pestulon|
|sci|Space Quest IV: Roger Wilco and the Time Rippers"// floppy is SCI1CD SCI1.1|
|sci|Space Quest V: The Next Mutation|
|agi|Space Quest X: The Lost Chapter|
|director|Spaceship Warlock|
|director|Spy Club|
|director|Spycraft: The Great Game|
|director|Star Trek Encyclopedia 1998|
|director|Star Trek Omnipedia|
|startrek|Star Trek: 25th Anniversary|
|director|Star Trek: Borg|
|director|Star Trek: Deep Space Nine Episode Guide|
|startrek|Star Trek: Judgment Rites|
|director|Star Trek: Klingon|
|director|Star Trek: The Next Generation Episode Guide|
|director|Star Trek: The Next Generation Interactive Technical Manual|
|titanic|Starship Titanic|
|director|Stay Tooned!|
|ags|Stickmen|
|wintermute|Strange Change|
|wintermute|Stroke of Fate: Operation Bunker|
|wintermute|Stroke of Fate: Operation Valkyrie|
|wintermute|Sunrise: The game|
|director|SuperSpy 1|
|ags|Superdisk|
|agos|Swampy Adventures|
|tads|TADS 2 Game|
|ags|TV Quest|
|wintermute|Tanya Grotter and the Disappearing Floor|
|wintermute|Tanya Grotter and the Magical Double Bass|
|teenagent|Teen Agent|
|groovie|Tender Loving Care|
|testbed|Testbed: The Backend Testing Framework|
|groovie|The 11th Hour: The Sequel to The 7th Guest|
|ags|The 6 Day Assassin|
|groovie|The 7th Guest|
|wintermute|The Ancient Mark - Episode 1|
|director|The ApartmentInteractive demo|
|sci|The Beast Within: A Gabriel Knight Mystery|
|parallaction|The Big Red Adventure|
|agi|The Black Cauldron|
|wintermute|The Box|
|director|The C.H.A.O.S. Continuum|
|sherlock|The Case of the Rose Tattoo|
|sherlock|The Case of the Serrated Scalpel|
|ags|The Crown of Gold|
|jacl|The Curse of Eldor"  // Competition 96|
|scumm|The Curse of Monkey Island|
|director|The Daedalus Encounter|
|director|The Dark Eye|
|sci|The Dating Pool|
|wintermute|The Death of Erin Myers|
|scumm|The Dig|
|wintermute|The Driller Incident|
|agos|The Feeble Files|
|sludge|The Game Jam Game About GamesSecrets and Stuff|
|sludge|The Game That Takes Place on a Cruise Ship|
|wintermute|The Golden Calf|
|griffon|The Griffon Legend|
|magnetic|The Guild of Thieves|
|director|The History of the United States for Young People|
|wintermute|The Idiot's Tale|
|ags|The Inexperienced Assassin|
|sludge|The Interview|
|ags|The Island|
|sci|The Island of Dr. Brain|
|director|The Journeyman Project|
|director|The Journeyman Project 2: Buried in Time|
|buried|The Journeyman Project 2: Buried in Time|
|pegasus|The Journeyman Project: Pegasus Prime|
|wintermute|The Kite|
|wintermute|The Last Crown - Midnight Horror|
|lastexpress|The Last Express|
|kyra|The Legend of Kyrandia|
|kyra|The Legend of Kyrandia: Malcolm's Revenge|
|kyra|The Legend of Kyrandia: The Hand of Fate|
|stark|The Longest Journey|
|wintermute|The Lost Crown - A Ghost-Hunting Adventure|
|tsage|The Lost Files of Sherlock Holmes (Logo)|
|director|The Magic Death|
|made|The Manhole|
|neverhood|The Neverhood Chronicles|
|pink|The Pink Panther: Hokus Pokus Pink|
|pink|The Pink Panther: Passport to Peril|
|prince|The Prince and the Coward|
|director|The Riddle of the Maze|
|ags|The Secret of Carver Island|
|scumm|The Secret of Monkey Island|
|sludge|The Secret of Tremendous Corporation|
|director|The Seven Colors: Legend of PSY-S City|
|wintermute|The Shine of a Star|
|director|The Simpsons: Cartoon Studio|
|director|The Simpsons: Cartoon Studio Player|
|ags|The Tower|
|wintermute|The Trader of Stories|
|ags|The Trials of Odysseus Kent|
|director|The Ultimate Einstein|
|director|The Ultimate Frank Lloyd Wright: America's Architect|
|nancy|The Vampire Diaries|
|ags|The Warp|
|wintermute|The Way Of Love: Sub Zero|
|wintermute|The White Chamber|
|director|The X-Files Unrestricted Access|
|ags|Thendor|
|ags|Tom Mato's Grand Wing-Ding|
|tony|Tony Tough and the Night of Roasted Moths|
|toon|Toonstruck|
|sci|Torin's Passage|
|director|Total Distortion|
|touche|Touche: The Adventures of the Fifth Musketeer|
|comprehend|Transylvania|
|director|Tri-3D-Trial|
|agi|Troll\'s Tale|
|ags|Tullie's World 1: The Roving of Candale|
|wage|Twisted!|
|director|Twisty Night #1|
|director|Twisty Night #2|
|director|Twisty Night #3|
|ultima|Ultima I - The First Age of Darkness|
|ultima|Ultima IV - Quest of the Avatar|
|ultima|Ultima IV - Quest of the Avatar - Enhanced|
|ultima|Ultima VI - The False Prophet|
|ultima|Ultima VI - The False Prophet - Enhanced|
|ultima|Ultima VIII - Pagan|
|groovie|Uncle Henry's Playhouse|
|sludge|Verb Coin|
|cryomni3d|Versailles 1685|
|director|Victor Vector & Yondo: The Cyberplasm Formula|
|director|Victor Vector & Yondo: The Hypnotic Harp|
|director|Victor Vector & Yondo: The Last Dinosaur Egg|
|director|Victor Vector & Yondo: The Vampire's Coffin|
|ags|VonLudwig|
|voyeur|Voyeur|
|wintermute|Vsevolod|
|wage|WAGE|
|wintermute|War|
|agos|Waxworks|
|sludge|Welcome Example|
|director|Who Killed Brett Penance?|
|director|Who Killed Sam Rupert?|
|director|Who Killed Taylor French? The Case of the Undressed Reporter|
|wintermute|Wilma Tetris|
|agi|Winnie the Pooh in the Hundred Acre Wood|
|wintermute|Wintermute 3D Characters Technology Demo|
|wintermute|Wintermute Engine Technology Demo|
|wintermute|Wintermute engine game|
|director|Wishbone and the Amazing Odyssey|
|magnetic|Wonderland|
|ultima|Worlds of Ultima: Martian Dreams|
|ultima|Worlds of Ultima: Martian Dreams - Enhanced|
|ultima|Worlds of Ultima: The Savage Empire|
|ultima|Worlds of Ultima: The Savage Empire - Enhanced|
|director|Wrath of the Gods|
|director|Xanthus|
|agi|Xmas Card|
|director|Yellow Brick Road|
|director|Yellow Brick Road II|
|director|Yellow Brick Road III|
|scumm|Zak McKracken & Loom|
|scumm|Zak McKracken and the Alien Mindbenders|
|wintermute|Zbang! The Game|
|director|Zeddas: Horror Tour 2|
|director|Zeddas: Servant of Sheol|
|wintermute|Zilm: A Game of Reflex|
|director|Zork Nemesis: The Forbidden Lands|
|zvision|Zork Nemesis: The Forbidden Lands|
|zvision|Zork: Grand Inquisitor|
|director|iD4 Mission Disk 1 - Alien Supreme Commander|
|director|iD4 Mission Disk 10 - Alien Bomber|
|director|iD4 Mission Disk 11 - Area 51|
|director|iD4 Mission Disk 2 - Alien Science Officer|
|director|iD4 Mission Disk 3 - Warrior Alien|
|director|iD4 Mission Disk 4 - Alien Navigator|
|director|iD4 Mission Disk 5 - Captain Steve Hiller|
|director|iD4 Mission Disk 6 - Dave's Computer|
|director|iD4 Mission Disk 7 - President Whitmore|
|director|iD4 Mission Disk 8 - Alien Attack Fighter|
|director|iD4 Mission Disk 9 - FA-18 Fighter Jet|
|magnetic|the Pawn|