# devlog

## wed 21 oct
started. got a menu, a room and one fight working. running away still lets the thing hit you. fixed that before stopping.

## wed 21 oct, later
second room. moved the rooms into a dict because the if/elif was already annoying. added the three types. shout beats song, song beats hush, hush beats shout.

## wed 21 oct, night
second creature and switching. phrases work once per fight. the enemy move is telegraphed now so it feels less like guessing. help screen added.

## fri 23 oct
finished the quiet house. the chalk on the door gives the party common speech, and the thing inside only flinches at a plain word, so every clever move leaves it standing. the porch gets your breath back, so losing there is not a dead end any more, and beating it prints the ending and clears the save. restart works at every prompt now. moved every printed line into rng/text.json so the writing can be changed without editing the code. wrote 37 tests and a scripted playthrough that reaches the end. went back through the wording: the opening was telling players three words were on a table when they were choosing creatures, the starter list now shows types, the command line finally mentions help and party, and the first fight explains its own menu once.
