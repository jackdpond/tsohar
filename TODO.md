1. Allow Index() to create Episode objects from paths and create a directory of Episode objects within the Index class.
2. Add docstrings and safety measures everywhere. Especially on API calls.
3. Maybe I want to accept a config file that organizes everything more easily, and adds everything from the config file containing paths. Have podcast name, series/season name, episode name.
4. Or different kinds of objects? That the index keeps track of? Podcasts, series, episodes? Each is like a directory?
5. Be mindful of default values and allow for more flexible file trees
6. Keep track of speakers (\*face-palm\*), fix in add_episode()