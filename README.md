# Quoridor
Text-based Quoridor board game made using Python.

5/24/25 - Currently working with all logic on local machines with Python 3.6+

5/27/26 - Revisited to add BFS path validation logic - still passing all tests and working OK.

7/7/26 - Finished the logic refactor to run on a webserver (but can still test locally with play.py)

8/4/26 - The UX upgrade: per-player fench markers, two-step fence placement flow, and clearer prompts for the web refactor.

9/27/26 - Game is deployed on Render.com server, with a postgres DB added to save in-progress games for if the server restarts or a new version is deployed

10/1/26 - Big UI/UX pass ahead of the v2.0 video: fence placement now previews before committing, join-by-name with shareable invite links, single-turn undo, a full move log, and a celebratory win screen.
