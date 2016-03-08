###CryptoIM

CryptoIM is a chat client that leverages the crypto Javascript library, new with ES6, to create RSA keys, and encrypt and decrypt messages in the browser. 

  - Allows users to chat, without sharing their raw messages with the server.
  - Allows users to know who is joining them to chat.
 
### Version
0.1.0

### Tech

CryptoIM is built on the following technologies and libraries:

* [PostgreSQL] - SQL open-source relational database.
* [Python] - Object-oriented programming language.
* [Flask] - Web framwork for Python.
* [Flask-SQLAlchemy] - Flask plugin to facilitate communication between the server and the PostgreSQL database.
* [Javascript] - Of course!
* [jQuery] - To make Javascript better!
* [Crypto] - Javascript crypto library new in ES6.
* [Twitter Bootstrap] - Great UI hooks for CSS to make a beautiful site quickly.

### Installation

First you'll need:
* [pip] - In order to find install all the python dependencies.
* [virtualenv] (recommended) - To keep all the dependancies in order

To get the server running:

1. Create a virtual environment.

2. Activate your virtual environment:
    ```sh
    $ <path_to_env>/bin/activate
    ```

3. Clone github repo:
    ```sh
    $ git clone https://github.com/KTAtkinson/crypto-im
    ```

4. Install python depencencies in your virtual env:
    ```sh
    $ pip install -r <path_to_project>/requirements.txt
    ```
5. Run the server:
    ```sh
    $ python <path_to_project>/server.py
    ```

6. Navigate to localhost:5000 in your web browser.

7. To stop the server type Ctrl+c in your terminal.

In order to have a conversation between two different users they must be in different browser sessions. The easiest way to do this is to have one window open in your session and another open in an incognito/in-private window.

### Todos
 * Add a help page.
 * Implement add chat button in upper right of chat page.
 * Allow encryption of long messages.
 * Store messages as base64 encoded text on server.
  
   
   [PostgreSQL]: <http://www.postgresql.org/>
   [Python]: <https://www.python.org/>
   [Flask]: <http://flask.pocoo.org/>
   [Flask-SQLAlchemy]: <http://flask-sqlalchemy.pocoo.org/2.1/>
   [Javascript]: <https://developer.mozilla.org/en-US/docs/Web/JavaScript>
   [Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>
   [Crypto]: <https://developer.mozilla.org/en-US/docs/Web/API/Window/crypto>
   [jQuery]: <http://jquery.com>
   [pip]: <https://pypi.python.org/pypi/pip>
   [virtualenv]: <https://virtualenv.readthedocs.org/en/latest/>


