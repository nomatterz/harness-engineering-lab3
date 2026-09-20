# Hard test set for embedding pipeline validation

Designed to actually stress semantic search, unlike sample_texts.md's clean topic separation. Each group below targets a specific failure mode a naive keyword search (or a weak embedding model) would trip on.

## Polysemy: python (language)

Python uses indentation instead of curly braces to define code blocks, which forces a consistent visual structure across a whole codebase.

## Polysemy: python (snake)

A python kills its prey by constriction, wrapping its body around the animal and tightening its coils with each exhale the prey takes.

## Polysemy: cell (biology)

A cell's mitochondria convert nutrients into ATP through a process called oxidative phosphorylation, powering nearly everything the cell does.

## Polysemy: cell (prison)

Inmates in solitary confinement spend up to twenty-three hours a day alone in a small cell, with limited human contact and no natural light.

## Same word, different domain: transaction (database)

A database transaction bundles several operations so they commit or roll back together, preventing a crash from leaving records half-updated.

## Same word, different domain: transaction (finance)

A wire transfer between banks can take one to three business days to settle, depending on the correspondent banking relationships involved.

## Paraphrase, no shared vocabulary: describes caching

Keeping a copy of frequently requested data somewhere faster to reach than its original source means future requests for that same data return almost instantly, at the cost of possibly serving something slightly out of date.

## Paraphrase, no shared vocabulary: describes garbage collection

A runtime can periodically walk through everything still reachable from a program's active variables and reclaim the memory behind anything no longer pointed to by them.

## Near-opposite meaning, similar wording: consistency achieved

Strong consistency guarantees that any read immediately after a write will see that write, no matter which replica answers the request.

## Near-opposite meaning, similar wording: consistency violated

Eventual consistency means a read immediately after a write might return stale data for a while, until replication catches up across all nodes.
