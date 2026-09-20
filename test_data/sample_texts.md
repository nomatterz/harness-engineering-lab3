# Sample texts for embedding pipeline validation

Each paragraph below is a separate chunk. Topics are grouped so retrieval correctness is easy to eyeball: a query about one topic should surface its group's paragraphs, not the others.

## Cooking

Searing a steak at high heat before finishing it in the oven creates a flavorful crust while keeping the inside tender. Letting the meat rest for five minutes after cooking allows the juices to redistribute evenly.

A good vinaigrette is usually three parts oil to one part acid, whisked with mustard as an emulsifier so it doesn't separate on the plate.

Fermenting vegetables like cabbage into sauerkraut relies on lactic acid bacteria naturally present on the produce, given enough salt and time in an anaerobic environment.

## Space travel

A rocket generates thrust by expelling mass at high velocity out of its engine nozzle, following Newton's third law — the exhaust pushes the vehicle forward as it pushes backward.

Getting into stable orbit requires reaching a sideways velocity high enough that the curve of your fall matches the curve of the planet, rather than just going straight up.

Astronauts on long missions lose bone density and muscle mass in microgravity, which is why they exercise for roughly two hours a day using resistance equipment on the station.

## Databases

An index speeds up read queries by letting the database jump directly to matching rows instead of scanning the whole table, at the cost of slightly slower writes since the index has to be updated too.

A transaction guarantees that a group of operations either all succeed or all fail together, so a crash partway through never leaves the data in a half-updated state.

Sharding splits a large dataset across multiple machines so no single server has to hold or serve all of it, usually partitioned by a key like user ID or region.
